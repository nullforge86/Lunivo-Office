"""Ring: aus ``vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler`` herausgelöst."""
from __future__ import annotations
import math
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QConicalGradient, QImage, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import QWidget
from vcl.qt.widgets.bausteine.abstaende.mass import STIFT_BETONT, STIFT_KREIS
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FARBRING
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler_hilfen import Modell


# ------------------------------------------------------------------------------------------------ Erweitert
class _Ring(QWidget):
    """Farbring (Farbton) mit Dreieck (Sättigung und Wert). Das Dreieck dreht mit: Die reine Farbe zeigt auf ihren Farbton."""
    AUSSEN, INNEN = 112.0, 90.0

    def __init__(self, modell: Modell):
        super().__init__()
        self.m = modell
        self.setFixedSize(*GROESSE_FARBRING)
        self.mitte = QPointF(self.width() / 2, self.height() / 2)
        self._ziehen = None                                      # "ring" oder "dreieck"
        self.m.geaendert.connect(self.update)

    def skaliere(self, k: float) -> None:
        """Ring und Dreieck im Maßstab ``k`` (1,0 = 270 × 250 Bildpunkte)."""
        self.AUSSEN, self.INNEN = 112.0 * k, 90.0 * k
        self.setFixedSize(int(270 * k), int(250 * k))
        self.mitte = QPointF(self.width() / 2, self.height() / 2)
        self.update()

    def _ecken(self) -> tuple[QPointF, QPointF, QPointF]:
        r = self.INNEN - 4
        t0 = self.m.h * 2 * math.pi
        def punkt(t): return QPointF(self.mitte.x() + r * math.sin(t), self.mitte.y() - r * math.cos(t))
        return punkt(t0), punkt(t0 + 2 * math.pi / 3), punkt(t0 + 4 * math.pi / 3)     # Farbe, Weiß, Schwarz

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        g = QConicalGradient(self.mitte, 90)
        for i in range(0, 361, 10):
            g.setColorAt(min(i / 360, 1.0), QColor.fromHsvF(((360 - i) % 360) / 360, 1, 1))
        ring = QPainterPath(); ring.addEllipse(self.mitte, self.AUSSEN, self.AUSSEN); ring.addEllipse(self.mitte, self.INNEN, self.INNEN)
        p.setPen(Qt.NoPen); p.fillPath(ring, QBrush(g))
        t = self.m.h * 2 * math.pi                               # Marke auf dem Ring
        mr = (self.AUSSEN + self.INNEN) / 2
        mp = QPointF(self.mitte.x() + mr * math.sin(t), self.mitte.y() - mr * math.cos(t))
        p.setBrush(Qt.NoBrush); p.setPen(QPen(QColor(Farbe.PAPIER), STIFT_KREIS)); p.drawEllipse(mp, 7, 7)
        p.setPen(QPen(QColor(Farbe.SCHWARZ), 1)); p.drawEllipse(mp, 8.5, 8.5)
        # Dreieck: Punkt für Punkt gemischt (a Farbe, b Weiß, c Schwarz)
        fa, fw, fk = self._ecken()
        links, oben = int(min(fa.x(), fw.x(), fk.x())) - 1, int(min(fa.y(), fw.y(), fk.y())) - 1
        rechts, unten = int(max(fa.x(), fw.x(), fk.x())) + 2, int(max(fa.y(), fw.y(), fk.y())) + 2
        bild = QImage(rechts - links, unten - oben, QImage.Format_ARGB32); bild.fill(Qt.transparent)
        reine = QColor.fromHsvF(min(self.m.h, 0.9999), 1, 1)
        for y in range(bild.height()):
            for x in range(bild.width()):
                a, b, c = self._schwerpunkt(QPointF(x + links, y + oben), fa, fw, fk)
                if a >= -0.01 and b >= -0.01 and c >= -0.01:
                    def kanal(wert: float) -> int: return min(255, max(0, round(255 * wert)))
                    bild.setPixelColor(x, y, QColor(kanal(a * reine.redF() + b), kanal(a * reine.greenF() + b), kanal(a * reine.blueF() + b)))
        spitze = QPainterPath(); spitze.addPolygon(QPolygonF([fa, fw, fk])); spitze.closeSubpath()
        p.setClipPath(spitze); p.drawImage(links, oben, bild); p.setClipping(False)
        p.setBrush(Qt.NoBrush); p.setPen(QPen(self.palette().mid().color(), 1)); p.drawPath(spitze)
        a, b = self.m.s * self.m.v, self.m.v * (1 - self.m.s)                     # Marke im Dreieck
        pos = QPointF(a * fa.x() + b * fw.x() + (1 - a - b) * fk.x(), a * fa.y() + b * fw.y() + (1 - a - b) * fk.y())
        p.setPen(QPen(QColor(Farbe.PAPIER), STIFT_BETONT)); p.drawEllipse(pos, 5, 5)
        p.setPen(QPen(QColor(Farbe.SCHWARZ), 1)); p.drawEllipse(pos, 6.5, 6.5)
        p.end()

    @staticmethod
    def _schwerpunkt(q: QPointF, a: QPointF, b: QPointF, c: QPointF) -> tuple[float, float, float]:
        d = (b.y() - c.y()) * (a.x() - c.x()) + (c.x() - b.x()) * (a.y() - c.y())
        u = ((b.y() - c.y()) * (q.x() - c.x()) + (c.x() - b.x()) * (q.y() - c.y())) / d
        v = ((c.y() - a.y()) * (q.x() - c.x()) + (a.x() - c.x()) * (q.y() - c.y())) / d
        return u, v, 1 - u - v

    def _wirke(self, pos) -> None:
        dx, dy = pos.x() - self.mitte.x(), pos.y() - self.mitte.y()
        if self._ziehen == "ring":
            self.m.setze_hsv(h=(math.atan2(dx, -dy) / (2 * math.pi)) % 1.0)
        elif self._ziehen == "dreieck":
            a, b, c = self._schwerpunkt(pos, *self._ecken())
            a, b, c = max(a, 0.0), max(b, 0.0), max(c, 0.0)
            summe = (a + b + c) or 1.0
            a, b = a / summe, b / summe
            v = a + b
            self.m.setze_hsv(s=(a / v) if v > 0 else self.m.s, v=v)

    def mousePressEvent(self, e):
        d = math.hypot(e.position().x() - self.mitte.x(), e.position().y() - self.mitte.y())
        self._ziehen = "ring" if self.INNEN - 2 <= d <= self.AUSSEN + 2 else "dreieck" if d < self.INNEN - 2 else None
        self._wirke(e.position())

    def mouseMoveEvent(self, e):
        self._wirke(e.position())

    def mouseReleaseEvent(self, _e):
        self._ziehen = None
