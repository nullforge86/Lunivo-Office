"""Das Fenster „Tabelleneigenschaften“ (Tabelle, Spalte, Zelle) als Baustein; formatiert nichts selbst.

    d = TabellenDialog(parent, werte)                    # ``werte`` wie ``editor.tabelleneigenschaften.lesen``
    if d.exec(): d.werte()
"""
from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QVBoxLayout, QWidget

from lunivo_writer.editor.tabelleneigenschaften import VORGABE
from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.formular_gitter import AngepassteReiter, FormularGitter, abschnittstitel
from lunivo_writer.ui.baukasten.mass_feld import EinheitFeld, spin
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

_BREITE = (("auto", "Automatisch"), ("prozent", "Prozent des Textbereichs"), ("fest", "Feste Breite"))
_AUSR = (("links", "Links"), ("mitte", "Zentriert"), ("rechts", "Rechts"))
_SENKRECHT = (("oben", "Oben"), ("mitte", "Mittig"), ("unten", "Unten"))


def _auswahl(eintraege) -> QComboBox:
    c = QComboBox()
    for k, name in eintraege:
        c.addItem(name, k)
    return c


class TabellenDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, werte: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Tabelleneigenschaften")
        w = {**VORGABE, **(werte or {})}
        v = QVBoxLayout(self)
        self.reiter = AngepassteReiter(); v.addWidget(self.reiter, 1)
        # ---- Tabelle
        s = QWidget(); g = FormularGitter(s)
        self.art = _auswahl(_BREITE); self.prozent = spin(100.0, 1.0, 100.0, " %", 1.0, 0)
        self.fest = EinheitFeld(0.0, 5.0, 1000.0, ("mm", "cm", "in"), "cm")
        self.ausr = _auswahl(_AUSR)
        g.reihe(("Breite:", self.art), ("Wert:", self.prozent), ("Wert:", self.fest))
        g.zeile("Ausrichtung:", self.ausr)
        g.breit(abschnittstitel("Zellen"))
        self.innen = EinheitFeld(0.0, 0.0, 50.0, ("mm", "cm", "pt"), "mm"); self.abstand = EinheitFeld(0.0, 0.0, 50.0, ("mm", "cm", "pt"), "mm")
        self.rahmen = EinheitFeld(0.0, 0.0, 5.0, ("mm", "pt"), "pt")
        g.reihe(("Innenabstand:", self.innen), ("Zellenabstand:", self.abstand))
        g.zeile("Rahmenstärke:", self.rahmen)
        self.reiter.addTab(s, "Tabelle")
        # ---- Spalte und Zelle (die der Schreibmarke)
        z = QWidget(); zg = FormularGitter(z)
        self.sp_fest = QCheckBox("Bevorzugte Breite der Spalte"); self.spalte = EinheitFeld(0.0, 5.0, 1000.0, ("mm", "cm", "in"), "cm")
        zg.breit(abschnittstitel("Spalte"))
        zg.breit(self.sp_fest); zg.zeile("Breite:", self.spalte)
        zg.breit(abschnittstitel("Zelle"))
        self.senkrecht = _auswahl(_SENKRECHT)
        zg.zeile("Senkrechte Ausrichtung:", self.senkrecht)
        self.reiter.addTab(z, "Spalte und Zelle")
        fussleiste(self, v)
        self.setze(w)
        self.art.currentIndexChanged.connect(self._sichtbar); self._sichtbar()

    def setze(self, w: dict) -> None:
        self.art.setCurrentIndex(max(0, self.art.findData(w["breite_art"])))
        if w["breite_art"] == "prozent":
            self.prozent.setValue(w["breite"])
        else:
            self.fest.setValue(w["breite"])
        self.ausr.setCurrentIndex(max(0, self.ausr.findData(w["ausr"])))
        self.innen.setValue(w["innen"]); self.abstand.setValue(w["abstand"]); self.rahmen.setValue(w["rahmen"])
        self.sp_fest.setChecked(bool(w["spalte_fest"])); self.spalte.setValue(w["spalte"] or 30.0)
        self.senkrecht.setCurrentIndex(max(0, self.senkrecht.findData(w["senkrecht"])))

    def _sichtbar(self, *_) -> None:
        a = self.art.currentData()
        self.prozent.setEnabled(a == "prozent"); self.fest.setEnabled(a == "fest")

    def werte(self) -> dict:
        a = self.art.currentData()
        return {"breite_art": a, "breite": self.prozent.value() if a == "prozent" else self.fest.value(), "ausr": self.ausr.currentData(),
                "innen": self.innen.value(), "abstand": self.abstand.value(), "rahmen": self.rahmen.value(),
                "spalte_fest": self.sp_fest.isChecked(), "spalte": self.spalte.value(), "senkrecht": self.senkrecht.currentData()}
