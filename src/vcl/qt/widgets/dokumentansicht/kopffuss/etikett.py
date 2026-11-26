"""Das Etikett „Kopfzeile“ / „Fußzeile“ am Rand des Bereichs: eine dezente Pille in der Akzentfarbe des Blatts. Der Text kommt vom Bearbeiter."""
from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget

from vcl.qt.widgets.bausteine.abstaende import KOPFFUSS_ETIKETT_RAND as KOPFFUSS_ETIKETT_INNENRAND
from vcl.qt.widgets.bausteine.farben import KOPFFUSS_ETIKETT_GRUND, KOPFFUSS_ETIKETT_RAND, KOPFFUSS_ETIKETT_TEXT


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
        waagerecht, senkrecht = KOPFFUSS_ETIKETT_INNENRAND
        m = self.fontMetrics()
        return QSize(m.horizontalAdvance(self._text) + waagerecht + waagerecht, m.height() + senkrecht + senkrecht)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        flaeche = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        p.setPen(QColor(KOPFFUSS_ETIKETT_RAND))                  # eine dezente Pille wie die Knöpfe daneben, kein gestrichelter Kasten
        p.setBrush(QColor(KOPFFUSS_ETIKETT_GRUND))
        p.drawRoundedRect(flaeche, flaeche.height() / 2, flaeche.height() / 2)
        p.setPen(QColor(KOPFFUSS_ETIKETT_TEXT))
        p.drawText(self.rect(), Qt.AlignCenter, self._text)
