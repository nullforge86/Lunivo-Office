"""Kanten flaeche: aus ``vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QSizePolicy, QWidget
from vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung_hilfen import _KANTE


class _KantenFlaeche(QWidget):
    """Die Vorschau mit den Kantenknöpfen um sich (oben, Mitte, unten links daneben; links und rechts darunter). Die Vorschau wächst mit
    der Breite bis ``maximal`` Bildpunkte, das Ganze steht in der Mitte und nimmt nie mehr Breite, als da ist."""

    def __init__(self, vorschau: QWidget, links: list, unten_l: QWidget, unten_r: QWidget):
        super().__init__()
        self.vorschau, self.links, self.unten_l, self.unten_r = vorschau, links, unten_l, unten_r
        for w in (vorschau, *links, unten_l, unten_r):
            w.setParent(self)
        self.maximal = 184
        sp = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum); sp.setHeightForWidth(True); self.setSizePolicy(sp)

    def _rand(self) -> int:
        return _KANTE + 6

    def _vorschau_breite(self, breite: int) -> int:
        return max(60, min(self.maximal, breite - self._rand()))

    def _vorschau_hoehe(self, w: int) -> int:
        n = len(self.links)
        return max(round(w * 118 / 184), n * _KANTE + (n - 1) * 4)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, breite: int) -> int:
        return self._vorschau_hoehe(self._vorschau_breite(breite)) + 4 + _KANTE

    def sizeHint(self) -> QSize:
        b = self.maximal + self._rand()
        return QSize(b, self.heightForWidth(b))

    def minimumSizeHint(self) -> QSize:
        b = 60 + self._rand()
        return QSize(b, self.heightForWidth(b))

    def setMaximal(self, maximal: int) -> None:
        self.maximal = maximal; self.updateGeometry(); self._lege()

    def resizeEvent(self, ev) -> None:
        self._lege()

    def _lege(self) -> None:
        w = self._vorschau_breite(self.width()); h = self._vorschau_hoehe(w)
        x0 = max(0, (self.width() - self._rand() - w) // 2)
        px = x0 + self._rand()
        self.vorschau.setGeometry(px, 0, w, h)
        n = len(self.links)
        for i, b in enumerate(self.links):
            b.setGeometry(x0, 0 if n == 1 else round(i * (h - _KANTE) / (n - 1)), _KANTE, _KANTE)
        self.unten_l.setGeometry(px, h + 4, _KANTE, _KANTE); self.unten_r.setGeometry(px + w - _KANTE, h + 4, _KANTE, _KANTE)
