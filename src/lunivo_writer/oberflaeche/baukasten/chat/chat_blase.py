"""Nachrichten des KI-Chats: Nutzerblase, KI-Antwort und Fehlerkarte — nur Darstellung, jede Aktion ruft den Dienst (``dienst``).

Aussehen kommt aus dem Thema (Karten-Arten ``nutzer``, ``ki``, ``fehler`` in ``karte.py``), Maße aus ``mass.py``. Die Bausteine kennen weder das Panel noch
den Editor: Ergebnisse melden sie über Signale (``vergleichOeffnen``, ``einstellungen``, ``inEingabe``). ``SymbolKnopf`` ist der Symbolknopf aller Chat-Bausteine."""
from __future__ import annotations

import os

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from lunivo_writer.ki import ki as K
from lunivo_writer.editor.text import ki_markdown
from lunivo_writer.oberflaeche.baukasten.basis.beschriftung import md_label, text_label
from lunivo_writer.oberflaeche.baukasten.dropdown.dropdown_knopf import DropdownKnopf
from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FlussLayout, abschnittstitel
from lunivo_writer.oberflaeche.baukasten.basis.karte import als_karte
from lunivo_writer.oberflaeche.baukasten.basis.zwischenablage import in_zwischenablage
from lunivo_writer.oberflaeche.baukasten.basis.mass import (
    ABSTAND_KLEIN, ABSTAND_NORMAL, CHAT_AUSZUG_ZEILEN, CHAT_KNOPF, CHAT_MINIATUR, CHAT_NUTZER_BLASE, CHAT_NUTZER_LEER, HOEHE_KNOPF_GROSS, ICON_NORMAL,
    RAND_BOX_KOMPAKT, RAND_KEIN)
from lunivo_writer.oberflaeche.baukasten.basis.texte import hinweis_label, hinweis_stil
from lunivo_writer.oberflaeche.bauteile import symbole


TITEL_NUTZER, TITEL_KI, TITEL_DOKUMENT = "Fragesteller", "KI", "Dokument"        # Beschriftung der Blasen: wer spricht bzw. was fürs Dokument ist
TEXT_VERGLEICH = "Vorher/Nachher öffnen"
TIPP_EINFUEGEN, TIPP_ERSETZEN = "Einfügen (Vorher/Nachher öffnen)", "Markierung oder überarbeitetes Dokument ersetzen (Vorher/Nachher öffnen)"
AUSLASSUNG, AUSLASSUNG_PUFFER = " …", 2         # Auslassungszeichen am Ende des Auszugs; Pufferzeilenhöhe in px


class SymbolKnopf(DropdownKnopf):
    """Flacher Symbolknopf (Chat): Symbol in Palettenfarbe, folgt dem Themenwechsel."""

    def __init__(self, symbol: str, tipp: str, funktion=None):
        super().__init__()
        self._symbol, self._farbe = symbol, None
        self.setToolTip(tipp); self.setAccessibleName(tipp); self.setAutoRaise(True); self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(CHAT_KNOPF, CHAT_KNOPF)
        if funktion is not None:
            self.clicked.connect(lambda _=False: funktion())
        self._zeichnen()

    def symbol_setzen(self, symbol: str, tipp: str | None = None, farbe: str | None = None) -> None:
        self._symbol, self._farbe = symbol, farbe
        if tipp is not None:
            self.setToolTip(tipp); self.setAccessibleName(tipp)
        self._zeichnen()

    def _zeichnen(self) -> None:
        self.setIcon(symbole.icon(self._symbol, ICON_NORMAL, self._farbe))

    def changeEvent(self, e) -> None:
        if e.type() in (QEvent.PaletteChange, QEvent.StyleChange) and hasattr(self, "_symbol"):
            self._zeichnen()
        super().changeEvent(e)


def miniatur(pfad: str, seite: int = CHAT_MINIATUR):
    """Kleine Bildvorschau als Widget. Fehlt die Datei oder lässt sie sich nicht lesen, steht dort der Platzhalter „[Bild]“."""
    pm = QPixmap(pfad) if pfad and os.path.isfile(pfad) else QPixmap()
    if pm.isNull():
        return hinweis_label("[Bild]", umbruch=False)
    l = QLabel(); als_karte(l, "miniatur")
    l.setPixmap(pm.scaled(QSize(seite, seite), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    l.setToolTip(os.path.basename(pfad)); l.setAlignment(Qt.AlignCenter)
    return l


def _text(text: str):
    t = text_label(text)
    t.setTextInteractionFlags(Qt.TextSelectableByMouse)
    return t


def antwort_label(text: str):
    """Antwort der KI: mit Überschriften, Listen, Tabellen oder Hervorhebungen als Markdown (dieselben Regeln wie bei der Übernahme ins Dokument,
    ``editor.text.ki_markdown``), sonst einfacher Text."""
    if not ki_markdown.hat_struktur(text):
        return _text(text)
    l = md_label(ki_markdown.normalisieren(text))
    l.setTextInteractionFlags(Qt.TextSelectableByMouse)
    return l


class NutzerBlase(QWidget):
    """Eigene Nachricht: rechts, grau, bei Anhang mit Bild-Miniatur; darunter Kopieren und Mehr (Text noch einmal ins Eingabefeld nehmen)."""
    inEingabe = Signal(str)

    def __init__(self, text: str, bilder: list | None = None):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN); v.setSpacing(ABSTAND_KLEIN)
        v.addWidget(abschnittstitel(TITEL_NUTZER), 0, Qt.AlignRight)
        zeile = QHBoxLayout(); zeile.setContentsMargins(*RAND_KEIN)
        rahmen = QFrame(); als_karte(rahmen, "nutzer")
        rv = QVBoxLayout(rahmen); rv.setContentsMargins(*RAND_BOX_KOMPAKT)
        for b in bilder or []:
            rv.addWidget(miniatur(b.get("pfad", "")), 0, Qt.AlignLeft)
        if text.strip() or not bilder:
            rv.addWidget(_text(text))
        zeile.addStretch(CHAT_NUTZER_LEER); zeile.addWidget(rahmen, CHAT_NUTZER_BLASE)
        v.addLayout(zeile)
        leiste = QHBoxLayout(); leiste.setContentsMargins(*RAND_KEIN); leiste.setSpacing(0)
        leiste.addStretch(1)
        leiste.addWidget(SymbolKnopf("copy", "Kopieren", lambda: in_zwischenablage(text)))
        mehr = SymbolKnopf("ellipsis", "Mehr")
        menue = MenueListe(mehr)
        menue.eintrag("Ins Eingabefeld übernehmen", lambda: self.inEingabe.emit(text), symbol=symbole.icon("text-cursor-input", ICON_NORMAL))
        mehr.menue_setzen(menue, geteilt=False)
        leiste.addWidget(mehr)
        v.addLayout(leiste)


class KiBlase(QWidget):
    """Antwort der KI mit Symbolzeile: Wiederholen, Kopieren, Einfügen, Ersetzen; Kosten klein dahinter.

    Der Dokumenttext steht kompakt in voller Breite (``TITEL_DOKUMENT``: Karte mit Auszug und dem Knopf „Vorher/Nachher öffnen“); Vergleich, Einfügen und
    Ersetzen laufen im ``AenderungsFenster`` (Seitenleiste, Signal ``vergleichOeffnen``) — es gibt genau einen Bestätigungsweg. Ob Einfügen/Ersetzen geht, sagt
    allein ``dienst.bezug_gueltig(index, ersetzen)``; ungültig = Symbole grau (Tooltip = Grund) und eine Hinweiszeile. ``index`` = Platz der Nachricht im Chat.

    ``dokument=False``: Einleitung oder Erklärung — kleine, ruhige Schrift, nur Kopieren, keine Dokumentaktionen.
    ``titel``: Beschriftung über der Blase (``TITEL_KI``); ohne Trennung (Titel „KI“) steht die Antwort als normaler Text da."""
    vergleichOeffnen = Signal(int)          # Kennung (``nr``) der Antwort; ``ai_panel`` öffnet damit ``w.kiVergleich``

    def __init__(self, dienst, text: str, cent=None, index: int = -1, *, dokument: bool = True, titel: str = ""):
        super().__init__()
        self.d, self.text, self.index, self.dokument = dienst, text, index, dokument
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN); v.setSpacing(ABSTAND_KLEIN)
        self.text_label = antwort_label(text)             # Antwort der KI: Text ohne Kasten, wie in der Vorlage
        if not dokument:
            hinweis_stil(self.text_label, klein=True)     # Erklärung: klein und gedämpft, das Dokument hat Vorrang
            if titel:
                v.addWidget(abschnittstitel(titel))
            v.addWidget(self.text_label)
            z = FlussLayout(ABSTAND_KLEIN)
            z.addWidget(SymbolKnopf("copy", "Kopieren", lambda: in_zwischenablage(text)))
            v.addLayout(z)
            return
        if titel == TITEL_DOKUMENT:                        # Dokumenttext: eine Karte mit Auszug und Knopf
            kasten = QFrame(); als_karte(kasten, "karte")
            kv0 = QVBoxLayout(kasten); kv0.setContentsMargins(*RAND_BOX_KOMPAKT); kv0.setSpacing(ABSTAND_KLEIN)
            kv0.addWidget(abschnittstitel(titel))
            self.auszug = self._auszug(text); kv0.addWidget(self.auszug)
            self.oeffnen = QPushButton(TEXT_VERGLEICH); self.oeffnen.setMinimumHeight(HOEHE_KNOPF_GROSS)
            self.oeffnen.clicked.connect(self.vergleich_oeffnen)
            kv0.addWidget(self.oeffnen)
            v.addWidget(kasten)
        else:
            if titel:
                v.addWidget(abschnittstitel(titel))
            v.addWidget(self.text_label)
        z = FlussLayout(ABSTAND_KLEIN)
        z.addWidget(SymbolKnopf("refresh-cw", "Antwort wiederholen", dienst.chat_wiederholen))
        z.addWidget(SymbolKnopf("copy", "Kopieren", lambda: in_zwischenablage(text)))
        self.einfuegen = SymbolKnopf("clipboard-paste", TIPP_EINFUEGEN, self.vergleich_oeffnen)
        z.addWidget(self.einfuegen)
        self.ersetzen = SymbolKnopf("replace", TIPP_ERSETZEN, self.vergleich_oeffnen)
        z.addWidget(self.ersetzen)
        if cent is not None:
            z.addWidget(hinweis_label(K.als_geld(cent), umbruch=False, klein=True))
        v.addLayout(z)
        self.hinweis = hinweis_label("", klein=True); self.hinweis.hide()
        v.addWidget(self.hinweis)
        self.kontext_neu()

    @staticmethod
    def _auszug(text: str):
        """Die ersten ``CHAT_AUSZUG_ZEILEN`` Zeilen des neuen Dokumenttexts; der Rest ist mit „…“ ausgelassen."""
        zeilen = [z for z in text.strip().splitlines() if z.strip()]
        kurz = "\n".join(zeilen[:CHAT_AUSZUG_ZEILEN]) + (AUSLASSUNG if len(zeilen) > CHAT_AUSZUG_ZEILEN else "")
        l = antwort_label(kurz)
        l.setMaximumHeight(CHAT_AUSZUG_ZEILEN * l.fontMetrics().lineSpacing() + AUSLASSUNG_PUFFER)       # lange Zeilen umbrechen nicht über den Auszug hinaus
        return l

    def vergleich_oeffnen(self) -> None:
        """Das Vergleichsfenster für diese Antwort anfordern (Signal ``vergleichOeffnen`` mit der Kennung; ohne Kennung nichts)."""
        nr = self.d.chat_modell.nachrichten[self.index].get("nr") if 0 <= self.index < len(self.d.chat_modell.nachrichten) else None
        if nr is not None:
            self.vergleichOeffnen.emit(nr)

    def kontext_neu(self) -> None:
        """Zustand der Symbole aus ``dienst.bezug_gueltig`` neu lesen (bei ``kontextGeaendert``/``chatGeaendert``)."""
        if not self.dokument:
            return
        ein_ok, ein_grund = self.d.bezug_gueltig(self.index, False)
        ers_ok, ers_grund = self.d.bezug_gueltig(self.index, True)
        for knopf, ok, grund, tipp in ((self.einfuegen, ein_ok, ein_grund, TIPP_EINFUEGEN), (self.ersetzen, ers_ok, ers_grund, TIPP_ERSETZEN)):
            knopf.setEnabled(ok); knopf.setToolTip(tipp if ok else grund)
        grund = "" if ein_ok else ein_grund
        self.hinweis.setText(grund); self.hinweis.setVisible(bool(grund))


class FehlerKarte(QWidget):
    """Fehler der KI: Titel, Text, Knopf „Wiederholen“; bei ``art`` „konfiguration“ der Weg zu den KI-Einstellungen, bei „zustimmung“ ein Hinweis."""
    einstellungen = Signal()

    def __init__(self, dienst, fehler: dict):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN)
        rahmen = QFrame(); als_karte(rahmen, "fehler")
        rv = QVBoxLayout(rahmen); rv.setSpacing(ABSTAND_NORMAL)
        rv.addWidget(text_label(fehler["titel"], fett=True))
        rv.addWidget(hinweis_label(fehler["text"]))
        art = fehler.get("art")
        if art == "zustimmung":
            rv.addWidget(hinweis_label("Beim Wiederholen wird die Zustimmung erneut abgefragt.", klein=True))
        z = FlussLayout(ABSTAND_NORMAL)
        if art == "konfiguration":
            b = QPushButton("KI-Einstellungen …"); b.clicked.connect(self.einstellungen.emit); z.addWidget(b)
        w = QPushButton("Wiederholen"); w.clicked.connect(lambda: dienst.chat_wiederholen()); z.addWidget(w)
        rv.addLayout(z)
        v.addWidget(rahmen)
