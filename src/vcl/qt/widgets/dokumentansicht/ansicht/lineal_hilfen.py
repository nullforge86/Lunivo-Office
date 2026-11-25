"""Lineal hilfen: aus ``vcl.qt.widgets.dokumentansicht.ansicht.lineal`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QPoint
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QWidget
from writer.werte import px_je_mm
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import SCHRIFT_LINEAL_PX


HOEHE = 26          # Dicke des Lineals


class _Lineal(QWidget):
    def __init__(self, tab):
        super().__init__(tab)
        self.tab = tab
        self.e = tab.editor
        self._zieh = None
        self._wert = None
        self.setMouseTracking(True)
        self.e.zoomChanged.connect(lambda *_: self.update())
        self.e.pageApplied.connect(self.update)
        self.e.cursorPositionChanged.connect(self.update)

    def _versatz(self) -> QPoint:
        """Wo der Editor (das Blatt) im Fenster steht — ändert sich beim Rollen."""
        return self.e.ansicht.mapTo(self.tab.viewport(), QPoint(0, 0))

    def px(self, mm: float) -> float:
        return mm * px_je_mm() * self.e.zoom

    def farben(self) -> dict:
        pal = self.palette()
        grund = pal.color(pal.ColorRole.Window)
        schrift = pal.color(pal.ColorRole.WindowText)
        dunkel = grund.darker(130) if grund.lightness() < 128 else grund.darker(108)
        hell = grund.lighter(125) if grund.lightness() < 128 else QColor(Farbe.WEISS)
        return {"grund": grund, "schrift": schrift, "aussen": dunkel, "text": hell}

    def _schrift(self, p: QPainter) -> None:
        f = QFont(p.font())
        f.setPixelSize(SCHRIFT_LINEAL_PX); f.setBold(False)
        p.setFont(f)
