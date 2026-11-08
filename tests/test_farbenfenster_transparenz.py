"""Fenster „Farben“: Transparenz (Schieber und Zahlenfeld in Prozent) gehört zur gewählten Farbe."""
from PySide6.QtGui import QColor

from lunivo_writer.ui.baukasten.farbwaehler import FarbenDialog


def test_transparenz_schieber_und_feld_gehen_in_die_farbe(app):
    d = FarbenDialog(None, QColor("#2f6fb5"), "Farben")
    assert d.schieber.value() == 100 == d.prozent.value() and d.farbe().alpha() == 255
    d.schieber.setValue(40)
    assert d.prozent.value() == 40 and abs(d.farbe().alphaF() - 0.4) < 0.01 and d.farbe().name() == "#2f6fb5"
    d.prozent.setValue(0)
    assert d.schieber.value() == 0 and d.farbe().alpha() == 0
    start = QColor("#ff0000"); start.setAlphaF(0.5)
    assert FarbenDialog(None, start).prozent.value() == 50
