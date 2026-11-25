"""Flaeche: aus ``vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen
from PySide6.QtWidgets import QWidget
from vcl.qt.widgets.bausteine.abstaende.mass import STIFT_BETONT
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FARBFLAECHE
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler_hilfen import Modell


# ------------------------------------------------------------------------------------------ Benutzerdefiniert
class _Flaeche(QWidget):
    """Farbton quer, Sättigung von oben (voll) nach unten (grau)."""
    def __init__(self, modell: Modell):
        super().__init__()
        self.m = modell
        self.setFixedSize(*GROESSE_FARBFLAECHE)
        self.bild = QImage(self.width(), self.height(), QImage.Format_RGB32)
        for y in range(self.height()):
            for x in range(self.width()):
                self.bild.setPixelColor(x, y, QColor.fromHsvF(x / self.width(), 1 - y / (self.height() - 1), 1.0))
        self.m.geaendert.connect(self.update)

    def setGroesse(self, b: int, h: int) -> None:
        """Größe ändern und das Farbbild neu rechnen."""
        self.setFixedSize(b, h)
        self.bild = QImage(b, h, QImage.Format_RGB32)
        for y in range(h):
            for x in range(b):
                self.bild.setPixelColor(x, y, QColor.fromHsvF(x / b, 1 - y / max(1, h - 1), 1.0))
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.drawImage(0, 0, self.bild)
        x, y = self.m.h * self.width(), (1 - self.m.s) * (self.height() - 1)
        p.setPen(QPen(QColor(Farbe.PAPIER), STIFT_BETONT)); p.setBrush(Qt.NoBrush); p.drawEllipse(QPointF(x, y), 6, 6)
        p.setPen(QPen(QColor(Farbe.SCHWARZ), 1)); p.drawEllipse(QPointF(x, y), 7.5, 7.5)
        p.end()

    def _setze(self, pos) -> None:
        self.m.setze_hsv(h=pos.x() / self.width(), s=1 - pos.y() / (self.height() - 1))

    def mousePressEvent(self, e): self._setze(e.position())
    def mouseMoveEvent(self, e): self._setze(e.position())
