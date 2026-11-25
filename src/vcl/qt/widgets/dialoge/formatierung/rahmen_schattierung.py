from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog, QDoubleSpinBox, QLabel
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel


def _kopf(text: str) -> QLabel:
    """Kleine Überschrift über einem Feld — der Baustein ``abschnittstitel``."""
    return abschnittstitel(text)


class _AbstandDialog(QDialog):
    """„Optionen …“ am Seitenrand: Abstand des Rahmens vom Seitenrand."""
    def __init__(self, parent, mm: float):
        super().__init__(parent)
        self.setWindowTitle("Rahmen- und Schattierungsoptionen")
        v = _spalte("standard", self)
        g = FormularGitter(); v.addLayout(g)
        self.feld = QDoubleSpinBox(); self.feld.setRange(2, 30); self.feld.setSuffix(" mm"); self.feld.setValue(mm)
        g.zeile("Abstand vom Seitenrand", self.feld)
        fussleiste(self, v)

    def wert(self) -> float:
        return self.feld.value()
