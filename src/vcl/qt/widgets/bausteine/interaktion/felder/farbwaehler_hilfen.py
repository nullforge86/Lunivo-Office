"""Farbwaehler hilfen: aus ``vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QObject, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QLabel, QWidget
from vcl.qt.widgets.bausteine.abstaende.mass import FARBWAEHLER_ZUGABE_LINKS, FARBWAEHLER_ZUGABE_RECHTS
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FARBPROBE, GROESSE_FARBREGLER
from framework.schnittstellen.datentypen.farben import Farbe


class Modell(QObject):
    """Die gewählte Farbe, als Farbton/Sättigung/Wert gehalten (der Farbton geht bei Grau nicht verloren)."""
    geaendert = Signal()
    modus_geaendert = Signal()

    def __init__(self, start: QColor):
        super().__init__()
        self.modus = "RGB"
        self.h, self.s, self.v = 0.0, 0.0, 0.0
        self.deckkraft = 100                                       # Transparenz-Feld: 100 % = deckend, 0 % = unsichtbar
        self.setze(start, melden=False)

    def farbe(self) -> QColor:
        return QColor.fromHsvF(min(self.h, 0.9999), self.s, self.v)

    def setze(self, c: QColor, melden: bool = True) -> None:
        c = QColor(c)
        h, s, v, _ = c.getHsvF()
        if h >= 0:
            self.h = h
        self.s, self.v = s, v
        if melden:
            self.geaendert.emit()

    def setze_deckkraft(self, prozent: int) -> None:
        prozent = min(max(int(prozent), 0), 100)
        if prozent != self.deckkraft:
            self.deckkraft = prozent
            self.geaendert.emit()

    def setze_hsv(self, h: float | None = None, s: float | None = None, v: float | None = None) -> None:
        if h is not None:
            self.h = min(max(h, 0.0), 0.9999)
        if s is not None:
            self.s = min(max(s, 0.0), 1.0)
        if v is not None:
            self.v = min(max(v, 0.0), 1.0)
        self.geaendert.emit()


class _Leiste(QWidget):
    """Helligkeit (Wert): oben hell, unten dunkel, mit Pfeil am rechten Rand."""
    def __init__(self, modell: Modell):
        super().__init__()
        self.m = modell
        self.setFixedSize(*GROESSE_FARBREGLER)
        self.m.geaendert.connect(self.update)

    def paintEvent(self, _e):
        p = QPainter(self)
        balken = QRectF(0, 0, 16, self.height())
        g = QLinearGradient(0, 0, 0, self.height()); g.setColorAt(0, QColor(Farbe.PAPIER)); g.setColorAt(1, QColor(Farbe.SCHWARZ))
        p.fillRect(balken, QBrush(g))
        y = (1 - self.m.v) * (self.height() - 1)
        pfeil = QPolygonF([QPointF(25, y - 5), QPointF(25, y + 5), QPointF(18, y)])
        p.setPen(Qt.NoPen); p.setBrush(self.palette().text()); p.drawPolygon(pfeil)
        p.end()

    def _setze(self, pos) -> None:
        self.m.setze_hsv(v=1 - pos.y() / (self.height() - 1))

    def mousePressEvent(self, e): self._setze(e.position())
    def mouseMoveEvent(self, e): self._setze(e.position())


# ----------------------------------------------------------------------------------------------------- Fenster
class _Proben(QWidget):
    """Eine Fläche, oben „Neu“, unten „Aktuell“."""
    def __init__(self, modell: Modell, aktuell: QColor):
        super().__init__()
        self.m, self.alt = modell, QColor(aktuell)
        self.setFixedSize(*GROESSE_FARBPROBE)
        self.m.geaendert.connect(self.update)

    def paintEvent(self, _e):
        p = QPainter(self)
        h = self.height() // 2
        for y in range(0, self.height(), 6):                      # Schachbrett: durch eine durchscheinende Farbe sieht man es
            for x in range(0, self.width(), 6):
                p.fillRect(x, y, 6, 6, QColor(Farbe.PAPIER) if (x // 6 + y // 6) % 2 == 0 else QColor(Farbe.LEISTE_RAND))
        neu = self.m.farbe(); neu.setAlphaF(self.m.deckkraft / 100)
        p.fillRect(0, 0, self.width(), h, neu)
        p.fillRect(0, h, self.width(), self.height() - h, self.alt)
        p.setPen(QPen(self.palette().mid().color(), 1)); p.setBrush(Qt.NoBrush); p.drawRect(0, 0, self.width() - 1, self.height() - 1)
        p.end()


class _FlaechePaar(QWidget):
    """Farbfläche und Helligkeitsleiste als ein Bedienelement; die Größe folgt den beiden (``ordne`` nach jeder Änderung)."""

    def __init__(self, flaeche: QWidget, leiste: QWidget):
        super().__init__()
        self.f, self.l = flaeche, leiste
        flaeche.setParent(self); leiste.setParent(self)
        self.ordne()

    def ordne(self) -> None:
        f, l = self.f, self.l
        h = max(f.height(), l.height())
        f.move(0, 0); l.move(f.width() + FARBWAEHLER_ZUGABE_LINKS, 0)
        self.setFixedSize(f.width() + FARBWAEHLER_ZUGABE_LINKS + l.width(), h)


class _ProbeBlock(QWidget):
    """Die Probe mit „Neu“ oben und „Aktuell“ unten daneben."""

    def __init__(self, probe: QWidget):
        super().__init__()
        probe.setParent(self)
        neu, alt = QLabel("Neu", self), QLabel("Aktuell", self)
        b = max(neu.sizeHint().width(), alt.sizeHint().width())
        probe.move(0, 0)
        neu.move(probe.width() + FARBWAEHLER_ZUGABE_RECHTS, 0)
        alt.move(probe.width() + FARBWAEHLER_ZUGABE_RECHTS, probe.height() - alt.sizeHint().height())
        self.setFixedSize(probe.width() + FARBWAEHLER_ZUGABE_RECHTS + b, probe.height())
