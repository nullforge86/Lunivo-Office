"""Positionen: aus ``vcl.qt.widgets.dialoge.dokument.liste_dialog`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from vcl.qt.widgets.bausteine.interaktion.felder.mass_feld import EinheitFeld
from vcl.qt.widgets.bausteine.abstaende.mass import RAND_DIALOG_GRUPPE
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import gruppe, FormularGitter


class _Positionen(QWidget):
    """Nummernposition (Ausrichtung der Nummer, Abstand) und Textposition (Tabstopp-Leerstelle nach, Einzug bei) — gemeinsam für
    „Nummerierung anpassen“ und „Gliederung anpassen“. Werte in Millimetern."""
    geaendert = Signal()

    def __init__(self):
        super().__init__()
        v = _spalte("standard", self)
        g1 = gruppe("Nummernposition"); a = FormularGitter(g1); a.setContentsMargins(*RAND_DIALOG_GRUPPE)
        self.art = Auswahlfeld()
        for k, name in (("links", "Links"), ("mitte", "Zentriert"), ("rechts", "Rechts")):
            self.art.addItem(name, k)
        self.ausr = EinheitFeld(0.0, 0.0, 300.0, ("mm", "cm", "in", "pt"))
        a.breit(self.art); a.zeile("Ausrichtung:", self.ausr)
        g2 = gruppe("Textposition"); t = FormularGitter(g2); t.setContentsMargins(*RAND_DIALOG_GRUPPE)
        self.tab = EinheitFeld(8.0, 0.0, 300.0, ("mm", "cm", "in", "pt")); self.einzug = EinheitFeld(8.0, 0.0, 300.0, ("mm", "cm", "in", "pt"))
        t.zeile("Tabstopp-Leerstelle nach:", self.tab); t.zeile("Einzug bei:", self.einzug)
        v.addWidget(g1); v.addWidget(g2)
        for sig in (self.art.currentIndexChanged, self.ausr.valueChanged, self.tab.valueChanged, self.einzug.valueChanged):
            sig.connect(lambda *_: self.geaendert.emit())

    def setze(self, ausr: float, art: str, tab: float, einzug: float) -> None:
        ws = (self.art, self.ausr, self.tab, self.einzug)
        for w in ws:
            w.blockSignals(True)
        self.art.setCurrentIndex(max(0, self.art.findData(art))); self.ausr.setValue(ausr); self.tab.setValue(tab); self.einzug.setValue(einzug)
        for w in ws:
            w.blockSignals(False)

    def werte(self) -> dict:
        return {"ausr": self.ausr.value(), "ausr_art": self.art.currentData(), "tab": self.tab.value(), "einzug": self.einzug.value()}
