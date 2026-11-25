"""Responsives Dashboard-Kachelraster auf der zentralen Grid-Fabrik."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_BLOCK, BREITE_KACHEL_MIN, RAND_KEIN, SPALTEN_KACHELN_MAX
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import tabellen_gitter


class Kachelraster(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._kacheln: list[tuple[QWidget, bool]] = []
        self._spalten = 0
        self._gitter = tabellen_gitter(self, rand=RAND_KEIN, abstand=ABSTAND_BLOCK)

    def hinzu(self, kachel: QWidget, ganze_breite: bool = False) -> None:
        self._kacheln.append((kachel, ganze_breite))
        self._ordnen(force=True)

    def _spaltenzahl(self) -> int:
        return max(1, min(SPALTEN_KACHELN_MAX, self.width() // BREITE_KACHEL_MIN))

    def _ordnen(self, force: bool = False) -> None:
        n = self._spaltenzahl()
        if n == self._spalten and not force:
            return
        self._spalten = n
        while self._gitter.count():
            self._gitter.takeAt(0)
        for s in range(SPALTEN_KACHELN_MAX):
            self._gitter.setColumnStretch(s, 1 if s < n else 0)
        zeile = spalte = 0
        for kachel, ganz in self._kacheln:
            if ganz and spalte:
                zeile += 1
                spalte = 0
            self._gitter.addWidget(kachel, zeile, spalte, 1, n if ganz else 1, Qt.AlignTop)
            spalte += n if ganz else 1
            if spalte >= n:
                zeile += 1
                spalte = 0
        self._gitter.setRowStretch(zeile + 1, 1)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._ordnen()
