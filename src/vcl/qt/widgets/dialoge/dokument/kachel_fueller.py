"""Kachel fueller: aus ``vcl.qt.widgets.dialoge.dokument.liste_dialog`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QEvent, QObject, QSize, Qt
from PySide6.QtWidgets import QListWidget


class _KachelFueller(QObject):
    """Ein Kachelraster füllt seine Breite mit drei Kacheln je Zeile (Größe folgt der Breite) und ist genau so hoch wie seine Zeilen."""

    def __init__(self, raster: QListWidget, spalten: int = 3):
        super().__init__(raster)
        self.r, self.spalten = raster, spalten
        raster.installEventFilter(self); raster.viewport().installEventFilter(self)      # auch die sichtbare Fläche: ihre Breite ist maßgebend
        raster.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); raster.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)       # die Höhe passt genau auf die Zeilen
        self._anpassen()

    def eventFilter(self, obj, ev) -> bool:
        try:
            if ev.type() == QEvent.Resize and obj in (self.r, self.r.viewport()):
                self._anpassen()
        except RuntimeError:                                       # das Raster wird gerade abgebaut
            pass
        return False

    def _anpassen(self) -> None:
        b = max(120, self.r.viewport().width() or self.r.width() - 4)
        zelle = (b - 6) // self.spalten
        icon = QSize(zelle - 8, int((zelle - 8) * 0.7))
        grid = QSize(zelle, icon.height() + 8)
        if self.r.gridSize() != grid:
            self.r.setIconSize(icon); self.r.setGridSize(grid)
        h = -(-self.r.count() // self.spalten) * grid.height() + 2 * self.r.frameWidth() + 6
        if self.r.height() != h:
            self.r.setFixedHeight(h)
