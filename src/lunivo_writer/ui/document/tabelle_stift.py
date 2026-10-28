"""„Tabelle zeichnen“ (Einfügen ▸ Tabelle): mit dem Stift ein Rechteck auf die Seite ziehen; gestrichelt erscheinen die Zellen und
ein Schild „Zeilen x Spalten“. Beim Loslassen kommt die Tabelle an die Stelle, wo das Ziehen begann. Esc oder Rechtsklick bricht ab.

    TabellenStift(editor)          # startet sofort; endet nach einer Tabelle oder mit Esc

Die Fläche liegt durchsichtig über dem Sichtbereich des Editors und fängt nur die Maus; das Dokument ändert erst ``insert_table``.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QRect, Qt
from PySide6.QtGui import QColor, QCursor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from lunivo_writer.core.farben import Farbe

ZELLE_B, ZELLE_H = 56, 20          # Zellengröße beim Zeichnen (Bildpunkte bei 100 %)


def groesse(breite: float, hoehe: float, zoom: float = 1.0) -> tuple[int, int]:
    """(Zeilen, Spalten) für ein gezogenes Rechteck; mindestens 1 × 1."""
    return max(1, round(hoehe / (ZELLE_H * zoom))), max(1, round(breite / (ZELLE_B * zoom)))


def _stift_cursor() -> QCursor:
    from lunivo_writer.ui.widgets import icons
    pm = icons.icon("stift", 24).pixmap(24, 24)
    return QCursor(pm, 2, pm.height() - 2) if not pm.isNull() else QCursor(Qt.CrossCursor)


class TabellenStift(QWidget):
    def __init__(self, ed):
        vp = ed.viewport()
        super().__init__(vp)
        self.ed = ed
        self._start: QPoint | None = None
        self._ende: QPoint | None = None
        self.setAttribute(Qt.WA_NoSystemBackground); self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(_stift_cursor())
        self.setFocusPolicy(Qt.StrongFocus)
        self.setGeometry(vp.rect())
        vp.installEventFilter(self)
        self.show(); self.raise_(); self.setFocus()
        fenster = ed.window()
        if hasattr(fenster, "statusBar"):
            fenster.statusBar().showMessage("Tabelle zeichnen: Rechteck aufziehen, Esc bricht ab.", 6000)

    def eventFilter(self, obj, ev) -> bool:
        if obj is self.ed.viewport() and ev.type() == QEvent.Resize:
            self.setGeometry(self.ed.viewport().rect())
        return False

    def _rechteck(self) -> QRect:
        return QRect(self._start, self._ende).normalized() if self._start and self._ende else QRect()

    def zellen(self) -> tuple[int, int]:
        r = self._rechteck()
        return groesse(r.width(), r.height(), getattr(self.ed, "zoom", 1.0))

    def mousePressEvent(self, e) -> None:
        if e.button() != Qt.LeftButton:
            self.beenden(); return
        self._start = self._ende = e.position().toPoint()
        self.update()

    def mouseMoveEvent(self, e) -> None:
        if self._start is not None:
            self._ende = e.position().toPoint(); self.update()

    def mouseReleaseEvent(self, e) -> None:
        if self._start is None or e.button() != Qt.LeftButton:
            return
        self._ende = e.position().toPoint()
        r = self._rechteck()
        if r.width() >= 8 and r.height() >= 8:
            zeilen, spalten = self.zellen()
            zoom = getattr(self.ed, "zoom", 1.0) or 1.0
            self.ed.setTextCursor(self.ed.cursorForPosition(self._start))
            self.ed.insert_table(zeilen, spalten, spaltenbreite=r.width() / spalten / zoom)
        self.beenden()

    def keyPressEvent(self, e) -> None:
        if e.key() == Qt.Key_Escape:
            self.beenden()
        else:
            super().keyPressEvent(e)

    def beenden(self) -> None:
        self.ed.viewport().removeEventFilter(self)
        self.hide(); self.deleteLater()
        self.ed.setFocus()

    def paintEvent(self, _e) -> None:
        r = self._rechteck()
        if r.isEmpty():
            return
        zeilen, spalten = self.zellen()
        p = QPainter(self)
        stift = QPen(QColor(Farbe.GRAU), 1, Qt.DashLine)
        p.setPen(stift)
        p.drawRect(r)
        for i in range(1, spalten):
            x = r.left() + r.width() * i // spalten; p.drawLine(x, r.top(), x, r.bottom())
        for i in range(1, zeilen):
            y = r.top() + r.height() * i // zeilen; p.drawLine(r.left(), y, r.right(), y)
        text = f"{zeilen}x{spalten}"
        fm = p.fontMetrics()
        schild = QRect(r.right() + 8, r.bottom() - fm.height() - 4, fm.horizontalAdvance(text) + 12, fm.height() + 4)
        p.fillRect(schild, QColor(Farbe.BLAU))
        p.setPen(QColor(Farbe.WEISS))
        p.drawText(schild, Qt.AlignCenter, text)
        p.end()
