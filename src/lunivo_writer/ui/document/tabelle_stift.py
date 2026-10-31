"""„Tabelle zeichnen“ (Einfügen ▸ Tabelle): mit dem Stift ein Rechteck auf die Seite ziehen; gestrichelt erscheinen die Zellen und
ein Schild „Zeilen x Spalten“. Beim Loslassen kommt die Tabelle an die Stelle, wo das Ziehen begann. Esc oder Rechtsklick bricht ab.

    TabellenStift(editor)          # startet sofort; endet nach einer Tabelle oder mit Esc

Die Maus wird programmweit abgefangen (Ereignisfilter an der Anwendung), solange der Stift aktiv ist, und der Stift-Mauszeiger gilt
überall (``setOverrideCursor``) — so funktioniert das Zeichnen auch, wenn über dem Sichtbereich andere Flächen liegen. Gezeichnet wird
die Vorschau auf einer durchsichtigen Fläche über dem Sichtbereich; das Dokument ändert erst ``insert_table``.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QRect, Qt
from PySide6.QtGui import QColor, QCursor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QApplication, QWidget

from lunivo_writer.core.farben import Farbe

ZELLE_B, ZELLE_H = 56, 20          # Zellengröße beim Zeichnen (Bildpunkte bei 100 %)


def groesse(breite: float, hoehe: float, zoom: float = 1.0) -> tuple[int, int]:
    """(Zeilen, Spalten) für ein gezogenes Rechteck; mindestens 1 × 1."""
    return max(1, round(hoehe / (ZELLE_H * zoom))), max(1, round(breite / (ZELLE_B * zoom)))


def _stift_cursor() -> QCursor:
    """Stift in Dunkel mit weißem Rand: auf weißem Blatt wie auf dunklem Grund gut zu sehen (Spitze oben links)."""
    from lunivo_writer.ui.widgets import icons
    px = 32
    hell, dunkel = (icons._pixmap("stift", f, px).scaled(px, px, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
                    for f in ("#ffffff", "#111111"))
    if hell.isNull():
        return QCursor(Qt.CrossCursor)
    bild = QImage(px + 8, px + 8, QImage.Format_ARGB32_Premultiplied)
    bild.fill(Qt.transparent)
    p = QPainter(bild)
    for dx in range(-2, 4):
        for dy in range(-2, 4):
            p.drawPixmap(3 + dx, 3 + dy, hell)             # weißer Rand um den verstärkten Strich
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        p.drawPixmap(3 + dx, 3 + dy, dunkel)
    p.end()
    pm = QPixmap.fromImage(bild)
    return QCursor(pm, 6, 6)


class TabellenStift(QWidget):
    MAUS = (QEvent.MouseButtonPress, QEvent.MouseMove, QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick)

    def __init__(self, ed):
        vp = ed.viewport()
        super().__init__(vp)
        self.ed = ed
        self._start: QPoint | None = None
        self._ende: QPoint | None = None
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setGeometry(vp.rect())
        self.show(); self.raise_()
        QApplication.setOverrideCursor(_stift_cursor())
        QApplication.instance().installEventFilter(self)
        self._aktiv = True
        fenster = ed.window()
        if hasattr(fenster, "statusBar"):
            fenster.statusBar().showMessage("Tabelle zeichnen: im Dokument ein Rechteck aufziehen. Esc oder Rechtsklick bricht ab.", 8000)

    def _im_dokument(self, global_pos) -> QPoint | None:
        vp = self.ed.viewport()
        pt = vp.mapFromGlobal(global_pos)
        return pt if vp.rect().contains(pt) else None

    def eventFilter(self, obj, ev) -> bool:
        t = ev.type()
        if not getattr(self, "_aktiv", False):
            return False
        if t == QEvent.KeyPress and ev.key() == Qt.Key_Escape:
            self.beenden(); return True
        if t not in self.MAUS or not isinstance(obj, QWidget) or obj.window() is not self.ed.window():
            return False
        gp = ev.globalPosition().toPoint()
        pt = self._im_dokument(gp)
        if t == QEvent.MouseButtonPress:
            if ev.button() != Qt.LeftButton:
                self.beenden(); return True
            if pt is None:                              # Klick außerhalb des Dokuments: Stift beenden, Klick normal weitergeben
                self.beenden(); return False
            self._start = self._ende = pt
            self.setGeometry(self.ed.viewport().rect()); self.raise_(); self.update()
            return True
        if t == QEvent.MouseMove:
            if self._start is not None:
                self._ende = self.ed.viewport().mapFromGlobal(gp); self.update()
            return pt is not None or self._start is not None
        if t == QEvent.MouseButtonRelease and self._start is not None:
            self._ende = self.ed.viewport().mapFromGlobal(gp)
            self._einfuegen()
            return True
        return pt is not None

    def _einfuegen(self) -> None:
        r = self._rechteck()
        if r.width() >= 8 and r.height() >= 8:
            zeilen, spalten = self.zellen()
            zoom = getattr(self.ed, "zoom", 1.0) or 1.0
            self.ed.setTextCursor(self.ed.cursorForPosition(self._start))
            self.ed.insert_table(zeilen, spalten, spaltenbreite=r.width() / spalten / zoom)
        self.beenden()

    def _rechteck(self) -> QRect:
        return QRect(self._start, self._ende).normalized() if self._start and self._ende else QRect()

    def zellen(self) -> tuple[int, int]:
        r = self._rechteck()
        return groesse(r.width(), r.height(), getattr(self.ed, "zoom", 1.0))

    def beenden(self) -> None:
        if not getattr(self, "_aktiv", False):
            return
        self._aktiv = False
        QApplication.instance().removeEventFilter(self)
        QApplication.restoreOverrideCursor()
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
