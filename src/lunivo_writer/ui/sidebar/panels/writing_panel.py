"""Bereich „Schreibhilfe“ der Seitenleiste: die Karten für Funde, Vorschläge und Hinweise."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout

from lunivo_writer.ui.baukasten.formular_gitter import FlussLayout

from lunivo_writer.ui.baukasten.beschriftung import md_escape, md_label, text_label
from lunivo_writer.ui.widgets import icons

import re

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.karte import als_karte
from lunivo_writer.models.proofing import ProofingIssue
from lunivo_writer.ui.baukasten.texte import hinweis_label
from lunivo_writer.ui.baukasten.mass import (
    ABSTAND_NORMAL,
    ICON_GROSS,
    PADDING_MARKE,
    RADIUS_MARKE,
    RAND_FUNDKARTE,
    RAND_KEIN,
    RAND_VORSCHLAGKARTE,
    SCHRIFT_KLEIN,
    SCHRIFT_LISTE,
)
_LAUF = re.compile(r"(.)\1{5,}")


def kurz(text: str) -> str:
    """Lange gleiche Zeichenfolgen (viele Leerzeichen hintereinander) kurz zeigen: „␣×34“ — sonst wird die Karte breiter als die Seitenleiste."""
    return _LAUF.sub(lambda m: f"{m.group(1)}×{len(m.group(0))}", text)


def farbe_je_art() -> dict:
    return {"fehler": Farbe.ORANGE, "tipp": Farbe.AUSWAHL, "hinweis": Farbe.GRAU}


# Marke oben auf der Karte: Schrift, Hintergrund (nach der Vorlage der ersten Fassung)
def _marken() -> dict:
    return {"fehler": ("SICHER FALSCH", Farbe.WARNUNG_HELL, Farbe.TINTE_DUNKEL), "tipp": ("KOMMT DRAUF AN", Farbe.AKZENT, Farbe.AUF_AKZENT),
            "hinweis": ("NUR ZUM NACHDENKEN", Farbe.GRAU, Farbe.AUF_AKZENT),
            "ki": ("KI-VORSCHLAG", Farbe.AKZENT_HELL, Farbe.TINTE_DUNKEL)}   # dunkle Schrift auf Hellblau: Kontrast ca. 5 : 1


def marke(art: str, quelle: str = "") -> QLabel:
    marken = _marken()
    text, grund, schrift = marken["ki"] if quelle == "ki" else marken.get(art, marken["hinweis"])
    m = QLabel(text)
    from lunivo_writer.ui.baukasten.texte import marke_faerben
    marke_faerben(m, grund, schrift, "border: none; border-radius: " f"{RADIUS_MARKE}" "px; padding: " f"{PADDING_MARKE}" "; font-size: " f"{SCHRIFT_KLEIN}" "pt; font-weight: 700; letter-spacing: 0.5px;")
    return m


class FundKarte(QFrame):
    def __init__(self, fund: ProofingIssue, assistent, parent=None, dienst=None):
        super().__init__(parent)
        self.fund, self.a, self.d = fund, assistent, dienst
        self.setObjectName("FundKarte")
        als_karte(self, "ki" if fund.quelle == "ki" else "karte")
        v = QVBoxLayout(self)
        v.setContentsMargins(*RAND_FUNDKARTE)
        v.setSpacing(ABSTAND_NORMAL)
        kopf = FlussLayout(6)
        kopf.addWidget(marke(fund.art, fund.quelle))
        v.addLayout(kopf)
        if fund.art != "hinweis" and fund.neu:
            t = md_label(f"~~{md_escape(kurz(fund.zeige_alt))}~~  →  **{md_escape(kurz(fund.zeige_neu))}**")
        else:
            t = text_label(f"„{kurz(fund.zeige_alt)[:80]}“" if fund.alt else "")
        t.setStyleSheet("border: none; background: transparent; font-size: " f"{SCHRIFT_LISTE}" "pt;")
        v.addWidget(t)
        g = hinweis_label(fund.grund, klein=True, zusatz="border: none; background: transparent;")
        v.addWidget(g)
        z = FlussLayout(6)
        zeigen = QPushButton("Zeigen")
        zeigen.clicked.connect(self._zeigen)
        z.addWidget(zeigen)
        if fund.art != "hinweis" and fund.neu:
            b = QPushButton("Ändern")
            b.clicked.connect(lambda: self.a.aendern(self.fund))
            z.addWidget(b)
        from lunivo_writer.services import vorlesen
        if vorlesen.verfuegbar():                                        # gleich neben den anderen Knöpfen: immer sichtbar
            ohr = QPushButton()
            ohr.setIcon(icons.icon("vorlesen", ICON_GROSS)); ohr.setCursor(Qt.PointingHandCursor)
            ohr.setToolTip("Das Wort anhören"); ohr.setAccessibleName("Das Wort anhören")
            ohr.clicked.connect(self._hoeren)
            z.addWidget(ohr)
        if fund.art == "hinweis" and fund.stelle and dienst is not None and fund.quelle != "ki":           # ein Hinweis auf einen Satz: die KI macht einen Vorschlag
            self.vorschlag_knopf = QPushButton("Vorschlag")
            self.vorschlag_knopf.setToolTip("Die KI schreibt den Satz kürzer — Sie nehmen es an oder verwerfen es")
            self.vorschlag_knopf.clicked.connect(self._vorschlag_holen)
            z.addWidget(self.vorschlag_knopf)
        self._aktionen = z
        for k in self.findChildren(QPushButton):
            pass
        v.addLayout(z)
        # Der Vorschlag der KI, erst sichtbar, wenn er da ist
        self.vorschlag_feld = QFrame(); self.vorschlag_feld.setStyleSheet("QFrame { border: none; background: transparent; }")
        vv = QVBoxLayout(self.vorschlag_feld); vv.setContentsMargins(*RAND_KEIN); vv.setSpacing(ABSTAND_NORMAL)
        self.vorschlag_text = QLabel(); self.vorschlag_text.setWordWrap(True); self.vorschlag_text.setStyleSheet("font-size: " f"{SCHRIFT_LISTE}" "pt; font-weight: 600;")
        vv.addWidget(self.vorschlag_text)
        vz = FlussLayout(6)
        self.annehmen = QPushButton("Annehmen"); self.annehmen.clicked.connect(self._annehmen)
        self.verwerfen = QPushButton("Verwerfen"); self.verwerfen.clicked.connect(self._verwerfen)
        for k in (self.annehmen, self.verwerfen):
            vz.addWidget(k)
        vv.addLayout(vz)
        self.vorschlag_feld.hide()
        v.addWidget(self.vorschlag_feld)

    def _vorschlag_holen(self):
        self.vorschlag_knopf.setEnabled(False); self.vorschlag_knopf.setText("Die KI schreibt …")
        self.d.satz_vorschlag(self.fund, self._vorschlag_da)
        if not self.d._beschaeftigt:                       # es kam nicht zum Lauf (kein Modell, kein Text): der Knopf bleibt bedienbar
            self.vorschlag_knopf.setEnabled(True); self.vorschlag_knopf.setText("Vorschlag")

    def _vorschlag_da(self, v: dict):
        try:
            self._v = v
            self.vorschlag_text.setText(v["neu"])
            self.vorschlag_feld.show()
            self.vorschlag_knopf.hide()
        except RuntimeError:                                 # die Karte gibt es nicht mehr (die Funde wurden inzwischen neu geholt)
            pass

    def _annehmen(self):
        if self.d.vorschlag_einsetzen(self._v):
            self.d.assistant.gelernt.ki_vermerken(self._v, True)
            self.a.pruefen(voll=True)                        # der Hinweis verschwindet, wenn der Satz kürzer ist

    def _verwerfen(self):
        self.d.assistant.gelernt.ki_vermerken(self._v, False)
        self.vorschlag_feld.hide()
        self.vorschlag_knopf.setEnabled(True); self.vorschlag_knopf.setText("Vorschlag"); self.vorschlag_knopf.show()

    def _zeigen(self):
        ed = self.a.editor
        if ed is not None:
            ed.select_range(self.fund.von, self.fund.bis)
            ed.setFocus()

    def _hoeren(self):
        from lunivo_writer.services import vorlesen
        f = self.fund
        vorlesen.lies_vor(f.zeige_neu if f.art != "hinweis" and f.neu else f.zeige_alt)

    def mousePressEvent(self, e):
        self._zeigen()
        super().mousePressEvent(e)


class VorschlagKarte(QFrame):
    def __init__(self, v: dict, dienst, panel):
        super().__init__()
        self.v, self.d, self.p = v, dienst, panel
        self.setObjectName("VorschlagKarte")
        als_karte(self, "karte")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(*RAND_VORSCHLAGKARTE)
        sicher = f" · Sicherheit {round(v['konfidenz'] * 100)} %" if "konfidenz" in v else ""
        g = hinweis_label(v.get("grund", "") + sicher, klein=True)
        t = md_label(f"~~{md_escape(v['alt'])}~~\n\n**{md_escape(v['neu'])}**")
        lay.addWidget(g); lay.addWidget(t)
        z = FlussLayout(6)
        b1 = QPushButton("Annehmen"); b1.clicked.connect(self._einsetzen)
        b2 = QPushButton("Verwerfen"); b2.clicked.connect(self._lassen)
        for k in (b1, b2):
            z.addWidget(k)
        lay.addLayout(z)

    def _lassen(self):
        self.d.assistant.gelernt.ki_vermerken(self.v, False)
        self._weg()

    def _einsetzen(self):
        if self.d.vorschlag_einsetzen(self.v):
            self.d.assistant.gelernt.ki_vermerken(self.v, True)
            self._weg()

    def _weg(self, abgelehnt: bool = False):
        self.hide(); self.setParent(None); self.deleteLater()


class HinweisKarte(QFrame):
    """Antworten, die den Text nicht ersetzen sollen (Zusammenfassung, Analyse)."""
    def __init__(self, titel, text, cent, fenster, panel):
        super().__init__()
        self.text, self.w = text, fenster
        self.setObjectName("HinweisKarte")
        als_karte(self, "karte")
        lay = QVBoxLayout(self)
        t = text_label(titel, fett=True, umbruch=False)
        body = text_label(text, auswaehlbar=True)
        lay.addWidget(t); lay.addWidget(body)
        z = FlussLayout(6)
        for name, fn in (("Kopieren", self._kopieren), ("Am Ende einfügen", self._ende), ("Schließen", self._weg)):
            b = QPushButton(name); b.clicked.connect(fn); z.addWidget(b)
        lay.addLayout(z)

    def _kopieren(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.text)

    def _ende(self):
        e = self.w.current_editor()
        if e is not None:
            c = e.textCursor(); c.movePosition(c.MoveOperation.End); c.insertBlock(); c.insertText(self.text)

    def _weg(self):
        self.hide(); self.setParent(None); self.deleteLater()
