"""Die gestrichelte Linie über die ganze Blattbreite, an der der Kopf- bzw. Fußbereich endet."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget

from vcl.qt.widgets.dokumentansicht.kopffuss.strich import strichstift


class KopfFussLinie(QWidget):
    def __init__(self, eltern: QWidget):
        super().__init__(eltern)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setPen(strichstift())
        p.drawLine(0, self.height() // 2, self.width(), self.height() // 2)
