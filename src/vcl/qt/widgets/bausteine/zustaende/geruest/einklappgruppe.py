"""Eingeklappte Gruppe („Weitere Einstellungen“): ein Knopf mit Pfeil, darunter der Inhalt, der erst auf Wunsch aufgeht.

Bedienbar mit Tab, Leertaste und Eingabetaste; ein Bildschirmleser meldet Namen und Zustand (ein-/ausgeklappt)."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import werkzeugknopf

from vcl.qt.widgets.bausteine.abstaende.raster import RasterSpalte
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QToolButton, QWidget
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_NORMAL, HOEHE_FELD, RAND_KEIN, RAND_ZEILE


class EinklappGruppe(QWidget):
    """Knopf plus Inhalt. Der Inhalt kommt in ``innen`` (ein ``RasterSpalte``)."""

    def __init__(self, titel: str = "Weitere Einstellungen", parent: QWidget | None = None):
        super().__init__(parent)
        self.titel = titel
        v = _spalte("zeile", self)
        self.knopf = werkzeugknopf("standard", umschaltbar=True)
        self.knopf.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.knopf.setText(titel)
        self.knopf.setMinimumHeight(HOEHE_FELD)
        self.knopf.setCursor(Qt.PointingHandCursor)
        self.knopf.setProperty("optName", titel)
        v.addWidget(self.knopf, 0, Qt.AlignLeft)
        self.inhalt = QWidget()
        self.innen = _spalte("standard", self.inhalt)
        v.addWidget(self.inhalt)
        self.knopf.toggled.connect(self._zeigen)
        self._zeigen(False)

    def _zeigen(self, offen: bool) -> None:
        self.inhalt.setVisible(offen)
        self.knopf.setArrowType(Qt.DownArrow if offen else Qt.RightArrow)
        self.knopf.setAccessibleName(f"{self.titel}, {'ausgeklappt' if offen else 'eingeklappt'}")

    def ausklappen(self, offen: bool = True) -> None:
        self.knopf.setChecked(offen)

    def ist_offen(self) -> bool:
        return self.knopf.isChecked()
