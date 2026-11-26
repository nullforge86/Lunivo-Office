"""Das Etikett „Kopfzeile“ / „Fußzeile“ am Rand des Bereichs: heller Grund, gestrichelter Rahmen, grauer Text. Der Text kommt vom Bearbeiter."""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from vcl.qt.widgets.bausteine.abstaende import KOPFFUSS_ETIKETT_RAND
from vcl.qt.widgets.bausteine.farben import KOPFFUSS_ETIKETT_GRUND, KOPFFUSS_ETIKETT_TEXT
from vcl.qt.widgets.dokumentansicht.kopffuss.strich import strichstift


class KopfFussEtikett(QWidget):
    def __init__(self, text: str, eltern: QWidget):
        super().__init__(eltern)
        self._text = ""
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.text_setzen(text)

    def text(self) -> str:
        return self._text

    def text_setzen(self, text: str) -> None:
        self._text = text
        self.setAccessibleName(text)
        self.resize(self.sizeHint())
        self.update()

    def sizeHint(self) -> QSize:
        waagerecht, senkrecht = KOPFFUSS_ETIKETT_RAND
        m = self.fontMetrics()
        return QSize(m.horizontalAdvance(self._text) + waagerecht + waagerecht, m.height() + senkrecht + senkrecht)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        flaeche = self.rect().adjusted(0, 0, -1, -1)
        p.fillRect(flaeche, QColor(KOPFFUSS_ETIKETT_GRUND))
        p.setPen(strichstift())
        p.drawRect(flaeche)
        p.setPen(QColor(KOPFFUSS_ETIKETT_TEXT))
        p.drawText(self.rect(), Qt.AlignCenter, self._text)
