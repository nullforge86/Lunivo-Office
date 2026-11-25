"""Kacheln: aus ``vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget
from vcl.qt.widgets.bausteine.abstaende.mass import FARBWAEHLER_ZUGABE_HOCH, RADIUS_ZEICHNUNG, RADIUS_ZEICHNUNG_GROSS, STIFT_BETONT
from vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler_hilfen import Modell


# ------------------------------------------------------------------------------------------------ Standard
class _Kacheln(QWidget):
    """Rundes Kachelraster: Farbton quer, oben hell und blass, unten dunkel; ganz unten die Graustufen."""
    bestaetigt = Signal()
    SPALTEN, ZEILEN, ZELLE, LUECKE = 17, 16, 14, 1

    def __init__(self, modell: Modell):
        super().__init__()
        self.m = modell
        self.skaliere(self.ZELLE)
        self.m.geaendert.connect(self.update)
        self.setMouseTracking(False)

    def skaliere(self, zelle: int) -> None:
        """Die Kacheln in dieser Größe (Bildpunkte) neu legen: so groß, wie Breite und Höhe der Seitenleiste es zulassen."""
        self.ZELLE = zelle
        self.LUECKE = 1 if zelle < 18 else 2
        schritt = self.ZELLE + self.LUECKE
        self.setFixedSize(self.SPALTEN * schritt + self.LUECKE, (self.ZEILEN + 2) * schritt + FARBWAEHLER_ZUGABE_HOCH)
        self.kacheln: list[tuple[QRectF, QColor]] = []
        for z in range(self.ZEILEN):
            for s in range(self.SPALTEN):
                hell = z < 8
                farbe = QColor.fromHsvF((s / self.SPALTEN), (z + 1) / 8 if hell else 1.0, 1.0 if hell else 1.0 - (z - 7) / 10)
                self.kacheln.append((self._feld(s, z), farbe))
        for i in range(12):                                        # Graustufen, weiß bis schwarz
            g = 1.0 - i / 11
            self.kacheln.append((self._feld(2 + i, self.ZEILEN + 0.6), QColor.fromHsvF(0, 0, g)))
        self.update()

    def _feld(self, s: float, z: float) -> QRectF:
        schritt = self.ZELLE + self.LUECKE
        return QRectF(self.LUECKE + s * schritt, self.LUECKE + z * schritt, self.ZELLE, self.ZELLE)

    def _bei(self, pos) -> QColor | None:
        for r, f in self.kacheln:
            if r.contains(pos):
                return f
        return None

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        jetzt = self.m.farbe().name()
        for r, f in self.kacheln:
            p.setPen(Qt.NoPen); p.setBrush(f)
            p.drawRoundedRect(r, RADIUS_ZEICHNUNG, RADIUS_ZEICHNUNG)
            if f.name() == jetzt:
                p.setBrush(Qt.NoBrush); p.setPen(QPen(self.palette().highlight().color(), STIFT_BETONT))
                p.drawRoundedRect(r.adjusted(-1.5, -1.5, 1.5, 1.5), RADIUS_ZEICHNUNG_GROSS, RADIUS_ZEICHNUNG_GROSS)
        p.end()

    def mousePressEvent(self, e):
        f = self._bei(e.position())
        if f is not None:
            self.m.setze(f)

    def mouseDoubleClickEvent(self, e):
        if self._bei(e.position()) is not None:
            self.bestaetigt.emit()
