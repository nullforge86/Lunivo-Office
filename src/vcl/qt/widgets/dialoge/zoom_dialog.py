"""Zoom dialog: aus ``vcl.qt.widgets.dialoge.dokument_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.option.option import option
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog, QSpinBox, QWidget
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
from vcl.qt.widgets.bausteine.abstaende.mass import RAND_KEIN


class ZoomDialog(PanelFaehig, QDialog):
    """Ansicht ▸ Zoom: feste Stufen, Seitenbreite, ganze Seite oder eigener Wert."""
    STUFEN = (200, 150, 100, 75, 50, 25)

    def __init__(self, parent, aktuell: float):
        super().__init__(parent)
        from PySide6.QtWidgets import QButtonGroup, QRadioButton, QSpinBox
        self.setWindowTitle("Zoom")
        lay = _spalte("standard", self)
        raster = QWidget(); fl = FlussLayout(10); raster.setLayout(fl); fl.setContentsMargins(*RAND_KEIN)
        self.gruppe = QButtonGroup(self)
        self._art: dict[int, tuple[str, float]] = {}
        eintraege = [(f"{n} %", ("wert", n / 100)) for n in self.STUFEN] + \
                    [("Seitenbreite", ("breite", 0)), ("Ganze Seite", ("seite", 0))]
        for i, (text, art) in enumerate(eintraege):
            r = option("standard", text)
            self.gruppe.addButton(r, i)
            self._art[i] = art
            fl.addWidget(r)
            if art[0] == "wert" and abs(art[1] - aktuell) < 0.005:
                r.setChecked(True)
        eigen = option("standard", "Eigener Wert:")
        self.gruppe.addButton(eigen, 100)
        self.spin = QSpinBox(); self.spin.setRange(10, 500); self.spin.setSuffix(" %")
        self.spin.setValue(int(round(aktuell * 100)))
        self.spin.valueChanged.connect(lambda _: eigen.setChecked(True))
        lay.addWidget(raster)
        ei = QWidget(); zeile = FormularGitter(ei); zeile.reihe(("", eigen), ("", self.spin))
        lay.addWidget(ei)
        if self.gruppe.checkedId() < 0:
            eigen.setChecked(True)
        bb = knopfzeile(self)
        lay.addWidget(bb)

    def ergebnis(self) -> tuple[str, float]:
        i = self.gruppe.checkedId()
        if i == 100 or i not in self._art:
            return "wert", self.spin.value() / 100
        return self._art[i]
