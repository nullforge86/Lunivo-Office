"""Farb feld: aus ``vcl.qt.widgets.menues.dropdown.auswahl.farbpalette`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QMenu, QPushButton
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_HOEHE
from vcl.qt.widgets.menues.dropdown.auswahl.farb_palette import FarbPalette


class FarbFeld(QPushButton):
    """Knopf für Dialoge, der seine Farbe zeigt; ein Klick öffnet die Palette. ``farbe`` ist ein Hex-Text ('' = keine)."""

    farbeGeaendert = Signal(str)
    verlaufGewaehlt = Signal(str)          # Farbe, die als Farbverlauf gemeint ist (nur mit ``verlauf=True``)

    def __init__(self, farbe: str | None = None, titel: str = "Farbe", keine_text: str | None = None, parent=None, verlauf: bool = False):
        super().__init__(parent)
        self.setMinimumHeight(DROPDOWN_HOEHE); self.setProperty("dropdownFeld", True)          # Höhe wie jedes Dropdown
        farbe = Farbe.SCHWARZ if farbe is None else farbe
        self.farbe, self.titel, self.keine_text, self._verlauf = farbe, titel, keine_text, verlauf
        self.clicked.connect(self._waehle)
        self._zeige()

    def setFarbe(self, farbe: str) -> None:
        self.farbe = farbe
        self._zeige()

    def _waehle(self) -> None:
        pal = FarbPalette(self, keine_text=self.keine_text, start=self.farbe or None, titel=self.titel, verlauf=self._verlauf)
        pal.gewaehlt.connect(self._uebernehmen)
        pal.verlauf_gewaehlt.connect(lambda c: self.verlaufGewaehlt.emit(c.name()))
        self._zeige_popup(pal)

    def _zeige_popup(self, pal: QMenu) -> None:
        pal.exec(self.mapToGlobal(QPoint(0, self.height())))

    def _uebernehmen(self, c: QColor | None) -> None:
        self.farbe = c.name() if c is not None else ""
        self._zeige()
        self.farbeGeaendert.emit(self.farbe)

    def _zeige(self) -> None:
        """Ruhig und sachlich: ein kleines Farbfeld mit Rand und der Name daneben — kein Knopf, der selbst bunt wird."""
        if not self.farbe:
            self.setText(self.keine_text or "Keine")
            pm = QPixmap(14, 14); pm.fill(Qt.transparent)
            p = QPainter(pm); p.setPen(QPen(QColor(Farbe.GRAU), 1)); p.drawRect(0, 0, 13, 13); p.drawLine(0, 13, 13, 0); p.end()
            self.setIcon(QIcon(pm))
        else:
            self.setText(self.farbe.upper())
            pm = QPixmap(14, 14); pm.fill(QColor(self.farbe))
            p = QPainter(pm); p.setPen(QPen(QColor(Farbe.GRAU), 1)); p.setBrush(Qt.NoBrush); p.drawRect(0, 0, 13, 13); p.end()
            self.setIcon(QIcon(pm))
        self.setProperty("feldknopf", True)
