"""Winkelfeld: Drehknopf (QDial) und Zähler „0,0°“ mit „−“ und „+“ (wie der Schattenwinkel der Vorlage).

    f = WinkelFeld(0.0, 360.0, "°", 1.0, 1, 0.0)    # lo, hi, Suffix, Schritt, Nachkommastellen, Wert
    f.value() · f.setValue(w) (meldet nichts) · f.valueChanged(float)   # nur bei Bedienung

Gleiche Schnittstelle wie ``SchiebeFeld``/``SchrittFeld`` (``schiebe_feld.py``); Knopf und Zähler bleiben synchron.
"""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDial, QHBoxLayout, QWidget

from lunivo_writer.ui.baukasten.schiebe_feld import SchrittFeld


class WinkelFeld(QWidget):
    valueChanged = Signal(float)

    def __init__(self, lo: float = 0.0, hi: float = 360.0, suffix: str = "°", schritt: float = 1.0, nachkomma: int = 1, wert: float = 0.0):
        super().__init__()
        self._lo, self._hi = lo, hi
        h = QHBoxLayout(self); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(8)
        self.knopf = QDial(); self.knopf.setRange(int(lo), int(hi)); self.knopf.setWrapping(True); self.knopf.setNotchesVisible(False)
        self.knopf.setFixedSize(36, 36)
        self.zaehler = SchrittFeld(lo, hi, suffix, schritt, nachkomma, wert)
        h.addWidget(self.knopf); h.addWidget(self.zaehler, 1)
        self.setValue(wert)
        self.knopf.valueChanged.connect(self._vom_knopf)
        self.zaehler.valueChanged.connect(self._vom_zaehler)

    def _vom_knopf(self, v: int) -> None:
        self.zaehler.blockSignals(True); self.zaehler.setValue(float(v)); self.zaehler.blockSignals(False)
        self.valueChanged.emit(float(v))

    def _vom_zaehler(self, v: float) -> None:
        self.knopf.blockSignals(True); self.knopf.setValue(int(round(v))); self.knopf.blockSignals(False)
        self.valueChanged.emit(v)

    def value(self) -> float:
        return self.zaehler.value()

    def setValue(self, v: float) -> None:
        v = max(self._lo, min(self._hi, float(v)))
        for x in (self.knopf, self.zaehler):
            x.blockSignals(True)
        self.knopf.setValue(int(round(v))); self.zaehler.setValue(v)
        for x in (self.knopf, self.zaehler):
            x.blockSignals(False)
