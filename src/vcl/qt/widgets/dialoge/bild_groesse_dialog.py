"""Bild groesse dialog: aus ``vcl.qt.widgets.dialoge.dokument_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.haken.haken import haken
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog, QWidget
from vcl.qt.widgets.bausteine.interaktion.felder.mass_feld import spin as _spin
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile


class BildGroesseDialog(PanelFaehig, QDialog):
    def __init__(self, breite_px: float, hoehe_px: float, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bildgröße")
        self.verh = (hoehe_px / breite_px) if breite_px else 1.0
        self.b = _spin(breite_px * 25.4 / 96, 1, 2000)
        self.h = _spin(hoehe_px * 25.4 / 96, 1, 2000)
        self.fest = haken("standard", "Seitenverhältnis beibehalten", an=True)
        self._sperre = False
        self.b.valueChanged.connect(self._b)
        self.h.valueChanged.connect(self._h)
        inhalt = QWidget(); form = FormularGitter(inhalt)
        form.reihe(("Breite", self.b), ("Höhe", self.h)); form.breit(self.fest)
        bb = knopfzeile(self)
        lay = _spalte("standard", self); lay.addWidget(inhalt); lay.addWidget(bb)

    def _b(self, v):
        if self.fest.isChecked() and not self._sperre:
            self._sperre = True; self.h.setValue(v * self.verh); self._sperre = False

    def _h(self, v):
        if self.fest.isChecked() and not self._sperre and self.verh:
            self._sperre = True; self.b.setValue(v / self.verh); self._sperre = False

    def breite_px(self): return self.b.value() * 96 / 25.4
    def hoehe_px(self): return self.h.value() * 96 / 25.4
