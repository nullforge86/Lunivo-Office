"""Rahmen schattierung hilfen: aus ``vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget
from vcl.qt.rendering.formen import Linie
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_RAHMENKANTEN_MIN, GROESSE_RAHMENKANTEN_WUNSCH
from vcl.qt.widgets.bausteine.abstaende.mass import STIFT_BILDCHEN


class _Vorschau(QWidget):
    """Blatt mit zwei Absätzen aus grauen Zeilen; zeigt Rahmen und Füllung und schaltet Kanten per Klick."""
    kante = Signal(str)

    def __init__(self, kanten_klick: bool = True):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)      # wächst und schrumpft mit seinem Platz
        self.seiten = ""
        self.linie = Linie()
        self.pinsel = None
        self.klick = kanten_klick
        self.mit_h = False                                        # Linie zwischen Absätzen schaltbar
        self.seitenrand: tuple[Linie, float] | None = None        # Rahmen um die Seite: (Linie, Abstand in mm)

    def sizeHint(self) -> QSize:
        return QSize(*GROESSE_RAHMENKANTEN_WUNSCH)

    def minimumSizeHint(self) -> QSize:
        return QSize(*GROESSE_RAHMENKANTEN_MIN)

    def _feld(self) -> QRectF:
        r = self.rect()
        return QRectF(r).adjusted(r.width() * 0.21, r.height() * 0.16, -r.width() * 0.21, -r.height() * 0.19)       # wie bei 220 × 160: 46 / 26 / 30 Bildpunkte

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(Farbe.PAPIER))
        f = self._feld()
        if self.seitenrand is not None:
            li, mm = self.seitenrand
            a = max(4.0, mm * 1.2)
            Linie(li.farbe, li.breite_pt, li.art, self.seiten).rahmen_zeichnen(p, QRectF(self.rect()).adjusted(a, a, -a, -a), 96 / 72)
            f = QRectF(self.rect()).adjusted(a + 14, a + 14, -a - 14, -a - 14)
        if self.pinsel is not None:
            p.fillRect(f, self.pinsel)
        p.setPen(Qt.NoPen); p.setBrush(QColor(Farbe.GRAU_HELL))
        zeilen = 7
        h = f.height() / (zeilen + 1)
        luecke = self._luecke(f)
        for i in range(zeilen):
            if i == 3:
                continue
            y = f.top() + h * (i + 0.5) + (h * 0.5 if i > 3 else 0)
            p.drawRect(QRectF(f.left() + 6, y, f.width() - 12 - (i in (2, 6)) * 40, h * 0.42))
        if self.seiten and self.seitenrand is None:
            self.linie.mit_seiten(self.seiten).rahmen_zeichnen(p, f, 96 / 72, [luecke])
        p.end()

    @staticmethod
    def _luecke(f: QRectF) -> float:
        return f.top() + f.height() / 8 * 3.5

    def mousePressEvent(self, e):
        if not self.klick:
            return
        f, pos, tol = self._feld(), e.position(), 9
        if self.seitenrand is not None:                           # beim Seitenrand sind die Kanten die des Seitenrahmens
            a = max(4.0, self.seitenrand[1] * 1.2)
            f = QRectF(self.rect()).adjusted(a, a, -a, -a)
        if not f.adjusted(-tol, -tol, tol, tol).contains(pos):
            return
        if self.mit_h and self.seitenrand is None and abs(pos.y() - self._luecke(f)) < tol * 1.4 and f.left() < pos.x() < f.right():
            self.kante.emit("h"); return
        for k, d in (("t", abs(pos.y() - f.top())), ("b", abs(pos.y() - f.bottom())), ("l", abs(pos.x() - f.left())), ("r", abs(pos.x() - f.right()))):
            if d < tol:
                self.kante.emit(k); return


# --------------------------------------------------------------------------------------------------- Karteireiter
_KANTE = 36                                                      # Größe der Kantenknöpfe


def _blatt_vorschau(p: QPainter, rect) -> tuple[QRectF, QRectF]:
    """Das Blatt der Optionen-Fenster: oben weiß, nach unten vom Feld abgeschnitten, darauf ein Textblock (die erste Zeile eingerückt).
    → (Blatt, Textblock) in Fensterkoordinaten."""
    r = QRectF(rect)
    blatt = QRectF(r.center().x() - 96, r.top(), 192, r.height() + 60)
    p.fillRect(blatt, QColor(Farbe.PAPIER)); p.setPen(QColor(Farbe.GRAU_HELL)); p.drawRect(blatt)
    text = QRectF(blatt.left() + 32, blatt.top() + 32, 128, 70)
    p.setPen(QPen(QColor(Farbe.GRAU), STIFT_BILDCHEN))
    y, n = text.top(), 0
    while y < text.bottom() - 0.5:
        p.drawLine(int(text.left() + (42 if n == 0 else 0)), int(y), int(text.right()), int(y)); y += 5; n += 1
    return blatt, text
