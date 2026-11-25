"""Zeichenraster: aus ``vcl.qt.widgets.dialoge.einfuegen.sonderzeichen`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QRect, QSize, Qt, Signal
from PySide6.QtGui import QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QSizePolicy, QWidget
from vcl.qt.widgets.bausteine.abstaende.mass import SCHRIFT_SONDERZEICHEN_PX
from vcl.qt.widgets.dialoge.einfuegen.sonderzeichen_hilfen import ZELLE


class Zeichenraster(QWidget):
    """Zeichen in Zellen, die sich der Breite anpassen: Spaltenzahl = Breite / Zelle, Höhe folgt der Zahl der Zeilen (``heightForWidth``)."""
    gewaehlt = Signal(int)
    gewaehlt_doppelt = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._zeichen: list[int] = []
        self._schrift = QFont(QApplication.font())
        self._aktuell = -1
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.setMinimumWidth(0)

    def setze(self, zeichen: list[int], schrift: QFont | None = None) -> None:
        self._zeichen = list(zeichen)
        if schrift is not None:
            self._schrift = QFont(schrift); self._schrift.setPixelSize(SCHRIFT_SONDERZEICHEN_PX)
        self._aktuell = -1
        self.updateGeometry(); self.update()

    def zeichen(self) -> list[int]:
        return self._zeichen

    def waehle(self, code: int | None) -> None:
        self._aktuell = self._zeichen.index(code) if code in self._zeichen else -1
        self.update()

    def spalten(self) -> int:
        return max(1, self.width() // ZELLE)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, breite: int) -> int:
        sp = max(1, breite // ZELLE)
        return max(1, -(-len(self._zeichen) // sp)) * ZELLE + 1

    def sizeHint(self) -> QSize:
        return QSize(ZELLE * 8 + 1, self.heightForWidth(ZELLE * 8))

    def minimumSizeHint(self) -> QSize:
        return QSize(ZELLE, ZELLE + 1)

    def zelle_von(self, i: int) -> QRect:
        sp = self.spalten()
        return QRect((i % sp) * ZELLE, (i // sp) * ZELLE, ZELLE, ZELLE)

    def paintEvent(self, _ev) -> None:
        p = QPainter(self)
        pal = self.palette()
        p.fillRect(self.rect(), pal.base())
        p.setFont(self._schrift)
        for i, cp in enumerate(self._zeichen):
            r = self.zelle_von(i)
            if i == self._aktuell:
                p.fillRect(r, pal.highlight() if self.hasFocus() else pal.midlight())
            p.setPen(QPen(pal.mid().color(), 1)); p.drawRect(r.adjusted(0, 0, -1, -1))
            p.setPen(pal.highlightedText().color() if i == self._aktuell and self.hasFocus() else pal.text().color())
            p.drawText(r, Qt.AlignCenter, chr(cp))
        p.end()

    def _index_bei(self, pos) -> int:
        i = (pos.y() // ZELLE) * self.spalten() + pos.x() // ZELLE
        return i if 0 <= i < len(self._zeichen) and pos.x() < self.spalten() * ZELLE else -1

    def mousePressEvent(self, ev) -> None:
        i = self._index_bei(ev.position().toPoint())
        if i >= 0:
            self._setze_index(i)
        self.setFocus(Qt.MouseFocusReason)

    def mouseDoubleClickEvent(self, ev) -> None:
        i = self._index_bei(ev.position().toPoint())
        if i >= 0:
            self.gewaehlt_doppelt.emit(self._zeichen[i])

    def _setze_index(self, i: int) -> None:
        self._aktuell = i
        self.update()
        self.gewaehlt.emit(self._zeichen[i])

    def keyPressEvent(self, ev) -> None:
        sp = self.spalten()
        schritt = {Qt.Key_Left: -1, Qt.Key_Right: 1, Qt.Key_Up: -sp, Qt.Key_Down: sp}.get(ev.key())
        if schritt is None or not self._zeichen:
            return super().keyPressEvent(ev)
        i = min(len(self._zeichen) - 1, max(0, (self._aktuell if self._aktuell >= 0 else 0) + (schritt if self._aktuell >= 0 else 0)))
        self._setze_index(i)

    def focusInEvent(self, ev) -> None:
        super().focusInEvent(ev); self.update()

    def focusOutEvent(self, ev) -> None:
        super().focusOutEvent(ev); self.update()
