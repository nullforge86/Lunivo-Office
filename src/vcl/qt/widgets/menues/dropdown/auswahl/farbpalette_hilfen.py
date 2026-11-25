"""Farbpalette hilfen: aus ``vcl.qt.widgets.menues.dropdown.auswahl.farbpalette`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_FARBKACHEL, DROPDOWN_INNEN_FARBE


class _Kachel(QWidget):
    """Ein Farbfeld der Palette; meldet Überfahren und Klick an die Palette."""

    def __init__(self, palette: "FarbPalette", farbe: str, seite: int = DROPDOWN_FARBKACHEL):
        super().__init__()
        self._p, self.farbe, self._an = palette, farbe, False
        self.setFixedSize(seite, seite)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(farbe)

    def enterEvent(self, e):
        self._an = True; self.update(); self._p.ueberfahren.emit(QColor(self.farbe))

    def leaveEvent(self, e):
        self._an = False; self.update(); self._p.verlassen.emit()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.rect().contains(e.position().toPoint()):
            self._p.waehle(QColor(self.farbe))

    def paintEvent(self, e):
        p = QPainter(self)
        r = QRectF(self.rect()).adjusted(DROPDOWN_INNEN_FARBE, DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE)
        p.fillRect(r, QColor(self.farbe))
        pal = self.palette()
        stift = QPen(pal.highlight().color() if self._an else pal.mid().color(), 2 if self._an else 1)
        p.setPen(stift); p.setBrush(Qt.NoBrush); p.drawRect(r)


class _VerlaufKachel(_Kachel):
    """Kachel der Zeile „Graduelle Füllung“: ein Farbverlauf von hell nach dunkel in der Farbe; ein Klick meldet die Farbe als Verlauf."""

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.rect().contains(e.position().toPoint()):
            self._p.verlauf_gewaehlt.emit(QColor(self.farbe)); self._p.close()

    def paintEvent(self, e):
        from PySide6.QtGui import QLinearGradient
        p = QPainter(self)
        r = QRectF(self.rect()).adjusted(DROPDOWN_INNEN_FARBE, DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE)
        g = QLinearGradient(r.topLeft(), r.bottomRight())
        g.setColorAt(0, QColor(self.farbe).lighter(150)); g.setColorAt(1, QColor(self.farbe).darker(140))
        p.fillRect(r, g)
        pal = self.palette()
        p.setPen(QPen(pal.highlight().color() if self._an else pal.mid().color(), 2 if self._an else 1)); p.setBrush(Qt.NoBrush); p.drawRect(r)


class _BildKachel(_Kachel):
    """Kachel einer Bildreihe („Musterfüllung“, „Strukturfüllung“): zeigt ein Bild; ein Klick meldet ihren Schlüssel."""

    def __init__(self, palette: "FarbPalette", schluessel: str, bild: QPixmap, tipp: str, seite: int = DROPDOWN_FARBKACHEL):
        super().__init__(palette, schluessel, seite)
        self._bild = bild; self.setToolTip(tipp)

    def enterEvent(self, e):
        self._an = True; self.update()

    def leaveEvent(self, e):
        self._an = False; self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self.rect().contains(e.position().toPoint()):
            self._p.reihe_gewaehlt.emit(self.farbe); self._p.close()

    def paintEvent(self, e):
        p = QPainter(self)
        r = QRectF(self.rect()).adjusted(DROPDOWN_INNEN_FARBE, DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE, -DROPDOWN_INNEN_FARBE)
        p.drawPixmap(r.toRect(), self._bild)
        pal = self.palette()
        p.setPen(QPen(pal.highlight().color() if self._an else pal.mid().color(), 2 if self._an else 1)); p.setBrush(Qt.NoBrush); p.drawRect(r)
