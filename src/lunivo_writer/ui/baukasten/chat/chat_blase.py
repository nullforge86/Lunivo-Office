"""Nachrichten des KI-Chats: Nutzerblase, KI-Antwort und Fehlerkarte — nur Darstellung, jede Aktion ruft den Dienst (``dienst``).

Aussehen kommt aus dem Thema (Karten-Arten ``nutzer``, ``ki``, ``fehler`` in ``karte.py``), Maße aus ``mass.py``. Die Bausteine kennen weder das Panel noch
den Editor: Ergebnisse melden sie über Signale (``meldung``, ``einstellungen``, ``inEingabe``). ``SymbolKnopf`` ist der Symbolknopf aller Chat-Bausteine."""
from __future__ import annotations

import os

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from lunivo_writer.ai import ki as K
from lunivo_writer.ui.baukasten.dokument.aenderungs_vorschau import AenderungsVorschau
from lunivo_writer.editor.text import ki_markdown
from lunivo_writer.ui.baukasten.basis.beschriftung import md_label, text_label
from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.controls.formular_gitter import FlussLayout
from lunivo_writer.ui.baukasten.basis.karte import als_karte
from lunivo_writer.ui.baukasten.basis.mass import ABSTAND_KLEIN, ABSTAND_NORMAL, CHAT_KNOPF, HOEHE_KNOPF_GROSS, CHAT_MINIATUR, ICON_NORMAL, RAND_KEIN
from lunivo_writer.ui.baukasten.basis.texte import hinweis_label
from lunivo_writer.ui.widgets import icons


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
        self.setIcon(icons.icon(self._symbol, ICON_NORMAL, self._farbe))

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


def _kopieren(text: str) -> None:
    QApplication.clipboard().setText(text)


class NutzerBlase(QWidget):
    """Eigene Nachricht: rechts, grau, bei Anhang mit Bild-Miniatur; darunter Kopieren und Mehr (Text noch einmal ins Eingabefeld nehmen)."""
    inEingabe = Signal(str)

    def __init__(self, text: str, bilder: list | None = None):
        super().__init__()
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN); v.setSpacing(ABSTAND_KLEIN)
        zeile = QHBoxLayout(); zeile.setContentsMargins(*RAND_KEIN)
        rahmen = QFrame(); als_karte(rahmen, "nutzer")
        rv = QVBoxLayout(rahmen)
        for b in bilder or []:
            rv.addWidget(miniatur(b.get("pfad", "")), 0, Qt.AlignLeft)
        if text.strip() or not bilder:
            rv.addWidget(_text(text))
        zeile.addStretch(1); zeile.addWidget(rahmen, 6)
        v.addLayout(zeile)
        leiste = QHBoxLayout(); leiste.setContentsMargins(*RAND_KEIN); leiste.setSpacing(0)
        leiste.addStretch(1)
        leiste.addWidget(SymbolKnopf("copy", "Kopieren", lambda: _kopieren(text)))
        mehr = SymbolKnopf("ellipsis", "Mehr")
        menue = MenueListe(mehr)
        menue.eintrag("Ins Eingabefeld übernehmen", lambda: self.inEingabe.emit(text), symbol=icons.icon("text-cursor-input", ICON_NORMAL))
        mehr.menue_setzen(menue, geteilt=False)
        leiste.addWidget(mehr)
        v.addLayout(leiste)


class KiBlase(QWidget):
    """Antwort der KI mit Symbolzeile: Wiederholen, Kopieren, Einfügen, Ersetzen; Kosten klein dahinter.

    Einfügen und Ersetzen klappen darunter eine Karte mit der Vorschau und „Übernehmen“/„Verwerfen“ auf. Ob das geht, sagt allein
    ``dienst.bezug_gueltig(index, ersetzen)``; ungültig = Knöpfe grau (Tooltip = Grund) und eine Hinweiszeile. ``index`` = Platz der Nachricht im Chat."""
    meldung = Signal(str)

    def __init__(self, dienst, text: str, cent=None, index: int = -1):
        super().__init__()
        self.d, self.text, self.index, self._ersetzen_modus = dienst, text, index, False
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN); v.setSpacing(ABSTAND_KLEIN)
        v.addWidget(antwort_label(text))                 # Antwort der KI: Text ohne Kasten, wie in der Vorlage
        z = FlussLayout(ABSTAND_KLEIN)
        z.addWidget(SymbolKnopf("refresh-cw", "Antwort wiederholen", dienst.chat_wiederholen))
        z.addWidget(SymbolKnopf("copy", "Kopieren", lambda: _kopieren(text)))
        self.einfuegen = SymbolKnopf("clipboard-paste", "An der Schreibmarke einfügen", lambda: self._oeffnen(False))
        z.addWidget(self.einfuegen)
        self.ersetzen = SymbolKnopf("replace", "Markierung durch die Antwort ersetzen", lambda: self._oeffnen(True))
        z.addWidget(self.ersetzen)
        if cent is not None:
            z.addWidget(hinweis_label(K.als_geld(cent), umbruch=False, klein=True))
        v.addLayout(z)
        self.hinweis = hinweis_label("", klein=True); self.hinweis.hide()
        v.addWidget(self.hinweis)
        self.karte = QFrame(); als_karte(self.karte, "karte"); self.karte.hide()
        kv = QVBoxLayout(self.karte); kv.setSpacing(ABSTAND_NORMAL)
        self.vorschau = AenderungsVorschau()
        kv.addWidget(self.vorschau)
        kz = FlussLayout(ABSTAND_NORMAL)
        self.uebernehmen = QPushButton("Übernehmen"); self.uebernehmen.setMinimumHeight(HOEHE_KNOPF_GROSS)
        self.uebernehmen.clicked.connect(self._uebernehmen)
        verwerfen = QPushButton("Verwerfen"); verwerfen.setMinimumHeight(HOEHE_KNOPF_GROSS)
        verwerfen.clicked.connect(self._schliessen)
        kz.addWidget(self.uebernehmen); kz.addWidget(verwerfen)
        kv.addLayout(kz)
        v.addWidget(self.karte)
        self.kontext_neu()

    def kontext_neu(self) -> None:
        """Zustand der Knöpfe aus ``dienst.bezug_gueltig`` neu lesen (bei ``kontextGeaendert``/``chatGeaendert``)."""
        ein_ok, ein_grund = self.d.bezug_gueltig(self.index, False)
        ers_ok, ers_grund = self.d.bezug_gueltig(self.index, True)
        for knopf, ok, grund, tipp in ((self.einfuegen, ein_ok, ein_grund, "An der Schreibmarke einfügen"),
                                       (self.ersetzen, ers_ok, ers_grund, "Markierung durch die Antwort ersetzen")):
            knopf.setEnabled(ok); knopf.setToolTip(tipp if ok else grund)
        offen_ok, offen_grund = (ers_ok, ers_grund) if self._ersetzen_modus else (ein_ok, ein_grund)
        self.uebernehmen.setEnabled(offen_ok); self.uebernehmen.setToolTip("" if offen_ok else offen_grund)
        grund = offen_grund if self.karte.isVisible() and not offen_ok else ("" if ein_ok else ein_grund)
        self.hinweis.setText(grund); self.hinweis.setVisible(bool(grund))

    def _oeffnen(self, ersetzen: bool) -> None:
        self._ersetzen_modus = ersetzen
        stuecke = self.d.antwort_vorschau(self.index, ersetzen)
        self.vorschau.stuecke_setzen(stuecke, markdown=ki_markdown.hat_struktur(self.text))
        self.karte.show()
        self.kontext_neu()

    def _schliessen(self) -> None:
        self.karte.hide()
        self.kontext_neu()

    def _uebernehmen(self) -> None:
        ok, meldung = (self.d.antwort_ersetzen if self._ersetzen_modus else self.d.antwort_einfuegen)(self.index)
        if ok:
            self._schliessen()
        elif meldung:
            self.meldung.emit(meldung)
            self.kontext_neu()


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
