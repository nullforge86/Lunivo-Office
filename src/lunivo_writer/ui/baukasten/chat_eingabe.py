"""Eingabekasten des KI-Chats: Textfeld, darunter + (Bild), Befehle (Meine Aktionen), Modellwahl und der runde Senden-/Stopp-Knopf; Fußzeile mit Hinweis.

Baut nur auf Bausteinen auf (Karte ``eingabe`` und ``senden`` aus ``karte.py``, ``Auswahlfeld``, ``SymbolKnopf``, Maße aus ``mass.py``); Farben und Rahmen kommen
aus dem Thema, der Fokusrahmen über die Eigenschaft ``fokus``. Die Logik bleibt im Dienst: der Kasten meldet ``senden(text)`` (dazu ``anhang()``), ``bild(text)``, ``stopp``, ``meldung(text)``."""
from __future__ import annotations

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QMessageBox, QPlainTextEdit, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ai import modellfaehigkeit as MF
from lunivo_writer.ui.baukasten.chat_anhang import AnhangChip
from lunivo_writer.ui.baukasten.chat_blase import SymbolKnopf
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.karte import als_karte
from lunivo_writer.ui.baukasten.mass import (ABSTAND_KLEIN, CHAT_EINGABE_MAX, CHAT_EINGABE_MIN, CHAT_SENDEN, DROPDOWN_ZEICHEN_KURZ, ICON_NORMAL, RAND_KEIN)
from lunivo_writer.ui.baukasten.texte import hinweis_label
from lunivo_writer.ui.widgets import icons

WERKZEUG_NAMEN = {"fragen": "Vor Ausführung fragen", "automatisch": "Automatisch genehmigen"}      # Reihenfolge wie ``MF.WERKZEUG_MODI``
PLATZHALTER = "Frag mich etwas …"
FUSSZEILE = "KI-Chat kann Fehler machen. Überprüfen Sie wichtige Informationen."


class ChatEingabe(QPlainTextEdit):
    """Mehrzeiliges Eingabefeld: Enter schickt ab, Umschalt+Enter macht eine neue Zeile; wächst mit dem Text bis ``CHAT_EINGABE_MAX``. ``text()``/``setText()`` wie beim Einzeiler."""
    abgeschickt = Signal()

    def __init__(self):
        super().__init__()
        self.setPlaceholderText(PLATZHALTER)
        self.setTabChangesFocus(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.document().documentLayout().documentSizeChanged.connect(lambda *_: self._hoehe())
        self._hoehe()

    def _hoehe(self) -> None:
        zeilen = max(1, int(self.document().documentLayout().documentSize().height()))
        h = zeilen * self.fontMetrics().lineSpacing() + 2 * int(self.document().documentMargin()) + 12
        self.setFixedHeight(max(CHAT_EINGABE_MIN, min(CHAT_EINGABE_MAX, h)))

    def keyPressEvent(self, e) -> None:
        if e.key() in (Qt.Key_Return, Qt.Key_Enter) and not (e.modifiers() & Qt.ShiftModifier):
            self.abgeschickt.emit()
            return
        super().keyPressEvent(e)

    def text(self) -> str:
        return self.toPlainText()

    def setText(self, t: str) -> None:
        self.setPlainText(t)
        self.moveCursor(QTextCursor.End)


class ChatEingabeKasten(QWidget):
    senden = Signal(str)
    bild = Signal(str)
    stopp = Signal()
    textGeaendert = Signal()
    meldung = Signal(str)                       # Hinweis für die Statuszeile (z. B. Anhang wegen Modellwechsel entfernt)
    neue_aktion = Signal()                      # „Neue Aktion …“ im Befehls-Menü; das Panel öffnet das vorhandene Fenster
    neuer_assistent = Signal()                  # „Neuer Assistent …“ im Befehls-Menü; das Panel ruft ``w.kiAssistentErstellen``

    def __init__(self, dienst):
        super().__init__()
        self.d = dienst
        self._frei, self._beschaeftigt = True, False
        self._anhang: AnhangChip | None = None
        aussen = QVBoxLayout(self); aussen.setContentsMargins(*RAND_KEIN); aussen.setSpacing(ABSTAND_KLEIN)
        self.kasten = QFrame(); als_karte(self.kasten, "eingabe"); self.kasten.setProperty("fokus", False)
        kv = QVBoxLayout(self.kasten); kv.setContentsMargins(ABSTAND_KLEIN, ABSTAND_KLEIN, ABSTAND_KLEIN, ABSTAND_KLEIN); kv.setSpacing(0)
        self.anhang_zeile = QVBoxLayout(); self.anhang_zeile.setContentsMargins(*RAND_KEIN); self.anhang_zeile.setSpacing(0)
        kv.addLayout(self.anhang_zeile)                       # leer, solange kein Bild angehängt ist
        self.eingabe = ChatEingabe()
        self.eingabe.installEventFilter(self)
        self.eingabe.abgeschickt.connect(self._abschicken)
        self.eingabe.textChanged.connect(self._zustand)
        self.eingabe.textChanged.connect(self.textGeaendert)
        kv.addWidget(self.eingabe)
        z = QHBoxLayout(); z.setContentsMargins(*RAND_KEIN); z.setSpacing(0)
        self.plus = SymbolKnopf("plus", "Mehr: Bild hinzufügen, Bild erzeugen, Websuche")
        self._plus_menue = MenueListe(self.plus)
        self._bild_eintrag = self._plus_menue.eintrag("Lokales Bild hinzufügen …", self._bild_waehlen, symbol=icons.icon("image-plus", ICON_NORMAL))
        self._plus_menue.eintrag("Bild aus Text erzeugen", lambda: self.bild.emit(self.eingabe.text().strip()),
                                 symbol=icons.icon("image", ICON_NORMAL), tip="Aus dem Text im Feld (oder der Markierung) ein Bild erzeugen und einfügen")
        self._websuche = self._plus_menue.schalter("Websuche", bool(self.d.konfig.websuche_optionen()["an"]), self._websuche_gewaehlt, symbol=icons.icon("globe", ICON_NORMAL))
        self._plus_menue.aboutToShow.connect(self._websuche_nachziehen)
        self._plus_menue.aboutToShow.connect(self._bild_nachziehen)
        self.plus.menue_setzen(self._plus_menue, geteilt=False)
        self.d.geaendert.connect(self._websuche_nachziehen)
        self.d.geaendert.connect(self._bild_nachziehen)
        self.befehle = SymbolKnopf("terminal", "Befehle und Meine Aktionen")
        self._menue = MenueListe(self.befehle); self._menue.aboutToShow.connect(self._aktionen_fuellen)
        self.befehle.menue_setzen(self._menue, geteilt=False)
        z.addWidget(self.plus); z.addWidget(self.befehle)
        self.modell = Auswahlfeld(min_zeichen=DROPDOWN_ZEICHEN_KURZ)
        self.modell.rolle("modell", "chat", mindest=True)
        self.modell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.modell.als_menue_nach_oben(zusatz=self._modell_zusatz)
        self.modell.setToolTip("KI-Modell für den Chat")
        self.modell.currentIndexChanged.connect(self._modell_gewaehlt)
        z.addWidget(self.modell, 1)
        self.knopf = QPushButton(); als_karte(self.knopf, "senden"); self.knopf.setFixedSize(CHAT_SENDEN, CHAT_SENDEN)
        self.knopf.setCursor(Qt.PointingHandCursor); self.knopf.clicked.connect(self._knopf)
        z.addWidget(self.knopf)
        kv.addLayout(z)
        aussen.addWidget(self.kasten)
        fuss = hinweis_label(FUSSZEILE, klein=True); fuss.setAlignment(Qt.AlignCenter)
        aussen.addWidget(fuss)
        self.modelle_neu()
        self._zustand()

    # ---- Anzeige
    def text(self) -> str:
        return self.eingabe.text()

    def setText(self, t: str) -> None:
        self.eingabe.setText(t); self.eingabe.setFocus()

    def leeren(self) -> None:
        self.eingabe.clear(); self.anhang_entfernen()

    # ---- Bild-Anhang
    def anhang(self) -> str | None:
        """Pfad des angehängten Bildes (oder ``None``)."""
        return self._anhang.pfad if self._anhang is not None else None

    def anhang_setzen(self, pfad: str, groesse: int) -> None:
        self.anhang_entfernen()
        self._anhang = AnhangChip(pfad, groesse)
        self._anhang.entfernt.connect(self.anhang_entfernen)
        self.anhang_zeile.addWidget(self._anhang)
        self._zustand()

    def anhang_entfernen(self) -> None:
        if self._anhang is not None:
            self._anhang.hide(); self._anhang.setParent(None); self._anhang.deleteLater(); self._anhang = None
            self._zustand()

    def _bild_waehlen(self) -> None:
        pfad, _ = QFileDialog.getOpenFileName(self, "Lokales Bild hinzufügen", "", "Bilder (*.png *.jpg *.jpeg *.webp)")
        if not pfad:
            return
        p = MF.bild_pruefen(pfad)                                 # Fehler (Format, Größe) meldet der Dienst beim Senden genauso; hier schon beim Anhängen
        if "fehler" in p:
            self.meldung.emit(p["fehler"]); return
        self.anhang_setzen(p["pfad"], p["bytes"])

    def _bild_nachziehen(self) -> None:
        """„Lokales Bild“ ist grau mit dem Hinweis des Dienstes, wenn das Modell keine Bilder kann; ein vorhandener Anhang fällt dann mit Hinweis weg."""
        kann = self.d.kann_bild()
        self._bild_eintrag.setEnabled(kann); self._bild_eintrag.setToolTip(self.d.bild_hinweis())
        if not kann and self._anhang is not None:
            self.anhang_entfernen()
            self.meldung.emit("Anhang entfernt: " + self.d.bild_hinweis())

    def zustand_setzen(self, frei: bool, beschaeftigt: bool) -> None:
        """``frei``: Modell verbunden (sonst alles gesperrt); ``beschaeftigt``: die KI arbeitet (Knopf wird zum Stopp)."""
        self._frei, self._beschaeftigt = frei, beschaeftigt
        self._zustand()

    def _zustand(self) -> None:
        has = bool(self.eingabe.text().strip())
        self.eingabe.setEnabled(self._frei)
        self.plus.setEnabled(self._frei and not self._beschaeftigt)
        self.befehle.setEnabled(self._frei and not self._beschaeftigt)
        self.modell.setEnabled(self._frei and not self._beschaeftigt)
        if self._anhang is not None:
            self._anhang.weg.setEnabled(not self._beschaeftigt)
        self.knopf.setEnabled(self._frei and (self._beschaeftigt or has or self._anhang is not None))
        self.knopf.setToolTip("Antwort stoppen" if self._beschaeftigt else "Senden")
        self.knopf.setAccessibleName(self.knopf.toolTip())
        self._symbole()

    def _symbole(self) -> None:
        self.knopf.setIcon(icons.icon("circle-stop" if self._beschaeftigt else "arrow-up", ICON_NORMAL, Farbe.AUF_AKZENT))

    def changeEvent(self, e) -> None:
        if e.type() in (QEvent.PaletteChange, QEvent.StyleChange) and hasattr(self, "knopf"):
            self._symbole()
        super().changeEvent(e)

    def eventFilter(self, o, e) -> bool:
        if o is self.eingabe and e.type() in (QEvent.FocusIn, QEvent.FocusOut):
            self.kasten.setProperty("fokus", e.type() == QEvent.FocusIn)
            self.kasten.style().unpolish(self.kasten); self.kasten.style().polish(self.kasten)          # Rahmenfarbe aus dem Thema neu lesen
        return super().eventFilter(o, e)

    # ---- Modellwahl und Befehle
    def modelle_neu(self) -> None:
        """Modellfeld aus der KI-Konfiguration füllen; „Standard“ zeigt den Namen des tatsächlich genutzten Modells."""
        from lunivo_writer.ui.dialogs.ki_dialoge import modell_felder_fuellen
        name = self.d.kontext()[3]
        modell_felder_fuellen(self.modell, self.d.konfig, "chatbot", standard=name or "Standard")

    def _modell_gewaehlt(self) -> None:
        self.d.konfig.aufgabe_setzen("chatbot", self.modell.currentData() or "")
        self.d.geaendert.emit()

    def _websuche_gewaehlt(self, an: bool) -> None:
        if bool(self.d.konfig.websuche_optionen()["an"]) != an:
            self.d.konfig.websuche_setzen(an=an)
            self.d.geaendert.emit()

    def _websuche_nachziehen(self) -> None:
        """Der Schalter zeigt immer den Zustand der Konfiguration (auch nach Änderungen in den Einstellungen)."""
        self._websuche.an_setzen(bool(self.d.konfig.websuche_optionen()["an"]))

    def _modell_zusatz(self, menue: MenueListe) -> None:
        """Zeilen unter der Modellliste: Denktiefe und Berechtigungen, je mit dem aktuellen Wert rechts und einem Untermenü. Grau mit Hinweis, wenn nicht möglich."""
        d = self.d
        stufe = d.denktiefe()
        sub = menue.untermenue("Denktiefe", icons.icon("brain", ICON_NORMAL), d.kann_denken(), wert=MF.DENKSTUFEN[stufe]["name"], tip=d.denken_hinweis())
        for k, v in MF.DENKSTUFEN.items():
            sub.eintrag(v["name"], lambda k=k: d.denktiefe_setzen(k), haken=k == stufe)
        modus = d.werkzeugmodus()
        sub = menue.untermenue("Berechtigungen", icons.icon("shield-check", ICON_NORMAL), d.werkzeuge_vorhanden(),
                               wert=WERKZEUG_NAMEN.get(modus, modus), tip=d.werkzeuge_hinweis())
        for k, name in WERKZEUG_NAMEN.items():
            sub.eintrag(name, lambda k=k: self._werkzeugmodus_waehlen(k), haken=k == modus)

    def _werkzeugmodus_waehlen(self, modus: str) -> None:
        if modus == "automatisch" and self.d.werkzeugmodus() != "automatisch":
            if QMessageBox.question(self, "Automatisch genehmigen", "Werkzeuge dürfen dann ohne Rückfrage lesen und schreiben. "
                                    "Löschen, Netzwerk und Unbekanntes fragen weiter. Das gilt nur für diese Sitzung.") != QMessageBox.Yes:
                return
        self.d.werkzeugmodus_setzen(modus)

    def _vorlagen_fuellen(self, menue: MenueListe) -> None:
        """Untermenü „Vorlagen“: dieselben Anweisungen wie die Chips (Datenquelle ``chat_vorschlaege``); Klick füllt das Eingabefeld."""
        from lunivo_writer.ai.chat_vorschlaege import chat_vorschlaege
        auswahl, leer = self.d.kontext()[:2]
        for e in chat_vorschlaege(auswahl, leer, self.d.konfig):
            if e["id"].startswith("assistent:"):
                continue
            menue.eintrag(e["titel"], lambda a=e["anweisung"]: self.setText(a), tip=e["hinweis"])

    def _aktionen_fuellen(self) -> None:
        for alt in self._menue.findChildren(MenueListe):
            alt.deleteLater()
        self._menue.clear()
        self._vorlagen_fuellen(self._menue.untermenue("Vorlagen"))
        self._menue.trenner()
        for a in self.d.konfig.assistenten("aktion"):
            self._menue.eintrag(a["name"].replace("&", "&&"), lambda a=a: self.d.assistent(a), tip=a["prompt"][:200])
        if not self.d.konfig.assistenten("aktion"):
            self._menue.eintrag("Noch keine eigenen Aktionen", aktiv=False)
        self._menue.eintrag("Neue Aktion …", self.neue_aktion.emit)
        self._menue.eintrag("Neuer Assistent …", self.neuer_assistent.emit)

    # ---- Senden
    def _abschicken(self) -> None:
        if self._frei and not self._beschaeftigt and (self.eingabe.text().strip() or self._anhang is not None):
            self.senden.emit(self.eingabe.text().strip())

    def _knopf(self) -> None:
        if self._beschaeftigt:
            self.stopp.emit()
        else:
            self._abschicken()
