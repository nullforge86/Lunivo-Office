"""„Radiergummi“ (Tabellentools): ein Klick auf eine Zellenlinie löscht sie; die beiden Zellen daneben werden zu einer verbunden.
Beim Überfahren erscheint die Linie unter der Maus rot. Esc oder Rechtsklick beendet den Radierer.

    TabellenRadierer(editor)       # startet sofort; die Löschung selbst macht ``tabelleneigenschaften.linie_loeschen``

Aufbau wie ``tabelle_stift.py``: Ereignisfilter an der Anwendung, eigener Mauszeiger (``setOverrideCursor``), durchsichtige Fläche für die Hervorhebung.
``kante_finden`` ist rein rechnerisch (Dokumentkoordinaten) und unabhängig von der Oberfläche.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QColor, QCursor, QImage, QPainter, QPen, QPixmap, QTextFormat
from PySide6.QtWidgets import QApplication, QWidget

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor.tabelle import tabelleneigenschaften as TE
from lunivo_writer.ui.document.tabelle.tabelle_stift import andere_beenden, cursor_zurueck, ueberwachen

TOLERANZ = 6.0          # Abstand zur Linie in Bildpunkten, bis zu dem sie getroffen wird


def _pad(zelle, name: str, tabelle) -> float:
    """Innenabstand der Zelle (links/oben); ohne eigenen Wert gilt der der Tabelle."""
    f = zelle.format()
    prop = {"links": QTextFormat.TableCellLeftPadding, "oben": QTextFormat.TableCellTopPadding}[name]
    return float(f.property(prop)) if f.hasProperty(prop) else tabelle.format().cellPadding()


def gitter(ed, t) -> tuple[list[float], list[float]]:
    """(x der Spaltengrenzen, y der Zeilengrenzen) der Tabelle in Dokumentkoordinaten, je ``columns+1`` bzw. ``rows+1`` Werte."""
    lay = ed.document().documentLayout()
    rahmen = lay.frameBoundingRect(t)
    f = t.format()
    halb = f.cellSpacing() / 2
    xs: list[float | None] = [None] * (t.columns() + 1)
    ys: list[float | None] = [None] * (t.rows() + 1)
    for r in range(t.rows()):
        for c in range(t.columns()):
            z = t.cellAt(r, c)
            if z.row() != r or z.column() != c:
                continue
            b = lay.blockBoundingRect(z.firstCursorPosition().block())
            x = b.left() - _pad(z, "links", t) - halb
            y = b.top() - _pad(z, "oben", t) - halb
            xs[c] = x if xs[c] is None else min(xs[c], x)
            ys[r] = y if ys[r] is None else min(ys[r], y)       # mittig/unten ausgerichtete Zellen sitzen tiefer: die oberste zählt
    xs[0], ys[0] = rahmen.left(), rahmen.top()
    xs[-1], ys[-1] = rahmen.right(), rahmen.bottom()
    for liste in (xs, ys):                                       # Lücken (nur verbundene Zellen): vom Vorgänger übernehmen
        for i, v in enumerate(liste):
            if v is None:
                liste[i] = liste[i - 1]
    return xs, ys                                                # type: ignore[return-value]


def kante_finden(ed, t, dx: float, dy: float, toleranz: float = TOLERANZ):
    """Nächste Zellenlinie zum Punkt (Dokumentkoordinaten): ``(zeile, spalte, seite, (x1, y1, x2, y2))`` oder ``None``.
    Zeile/Spalte nennen die Zelle, an deren ``seite`` (links/rechts/oben/unten) die Linie liegt."""
    xs, ys = gitter(ed, t)
    beste, abstand = None, toleranz
    gesehen = set()
    for r in range(t.rows()):
        for c in range(t.columns()):
            z = t.cellAt(r, c)
            if z.row() != r or z.column() != c or (r, c) in gesehen:
                continue
            gesehen.add((r, c))
            c1, r1 = min(c + z.columnSpan(), t.columns()), min(r + z.rowSpan(), t.rows())
            x0, x1, y0, y1 = xs[c], xs[c1], ys[r], ys[r1]
            for seite, d, innen, linie in (
                    ("links", abs(dx - x0), y0 <= dy <= y1, (x0, y0, x0, y1)), ("rechts", abs(dx - x1), y0 <= dy <= y1, (x1, y0, x1, y1)),
                    ("oben", abs(dy - y0), x0 <= dx <= x1, (x0, y0, x1, y0)), ("unten", abs(dy - y1), x0 <= dx <= x1, (x0, y1, x1, y1))):
                if innen and d < abstand:
                    beste, abstand = (r, c, seite, linie), d
    return beste


def _radierer_cursor() -> QCursor:
    """Radiergummi in Dunkel mit weißem Rand (wie der Stift): auf weißem Blatt wie auf dunklem Grund gut zu sehen; heißer Punkt unten links."""
    from lunivo_writer.ui.widgets import icons
    px = 32
    hell, dunkel = (icons._pixmap("eraser", f, px).scaled(px, px, Qt.IgnoreAspectRatio, Qt.SmoothTransformation) for f in (Farbe.WEISS, Farbe.SCHWARZ))
    if hell.isNull():
        return QCursor(Qt.CrossCursor)
    bild = QImage(px + 8, px + 8, QImage.Format_ARGB32_Premultiplied)
    bild.fill(Qt.transparent)
    p = QPainter(bild)
    for dx in range(-2, 4):
        for dy in range(-2, 4):
            p.drawPixmap(3 + dx, 3 + dy, hell)
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        p.drawPixmap(3 + dx, 3 + dy, dunkel)
    p.end()
    return QCursor(QPixmap.fromImage(bild), 6, px - 2)


class TabellenRadierer(QWidget):
    MAUS = (QEvent.MouseButtonPress, QEvent.MouseMove, QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick)

    def __init__(self, ed):
        vp = ed.viewport()
        andere_beenden(ed)
        super().__init__(vp)
        self.ed = ed
        self._linie: tuple[float, float, float, float] | None = None       # Hervorhebung in Bildpunkten des Sichtbereichs
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setGeometry(vp.rect())
        self.show(); self.raise_()
        QApplication.setOverrideCursor(_radierer_cursor())
        QApplication.instance().installEventFilter(self)
        self._aktiv = True
        ueberwachen(self, ed, bei_tabellenverlust=True)
        fenster = ed.window()
        if hasattr(fenster, "statusBar"):
            fenster.statusBar().showMessage("Radiergummi: auf eine Zellenlinie klicken. Esc oder Rechtsklick beendet.", 8000)

    # ---- Koordinaten -----------------------------------------------------------------------------------------------
    def _doc(self, pt: QPoint) -> tuple[float, float]:
        ed = self.ed
        if ed._blatt_aktiv():
            return ed._sp_doc(pt.x(), pt.y())
        return pt.x() + ed.horizontalScrollBar().value(), pt.y() + ed.verticalScrollBar().value()

    def _view(self, x: float, y: float) -> tuple[float, float]:
        ed = self.ed
        if ed._blatt_aktiv():
            return ed._sp_view(x, y)
        return x - ed.horizontalScrollBar().value(), y - ed.verticalScrollBar().value()

    def treffer(self, pt: QPoint):
        """Die Linie unter dem Punkt des Sichtbereichs: ``(tabelle, (zeile, spalte, seite, linie))`` oder ``None``."""
        c = self.ed.cursorForPosition(pt)
        t = c.currentTable()
        if t is None:
            return None
        k = kante_finden(self.ed, t, *self._doc(pt))
        return (t, k) if k else None

    def _im_dokument(self, global_pos) -> QPoint | None:
        vp = self.ed.viewport()
        pt = vp.mapFromGlobal(global_pos)
        return pt if vp.rect().contains(pt) else None

    # ---- Ereignisse ------------------------------------------------------------------------------------------------
    def eventFilter(self, obj, ev) -> bool:
        t = ev.type()
        if not getattr(self, "_aktiv", False):
            return False
        if t in (QEvent.Hide, QEvent.Close) and obj in (self.ed, self.ed.window()):      # Dokumentwechsel oder Fenster schließt
            self.beenden(); return False
        if t == QEvent.KeyPress and ev.key() == Qt.Key_Escape:
            self.beenden(); return True
        if t not in self.MAUS or not isinstance(obj, QWidget) or obj.window() is not self.ed.window():
            return False
        pt = self._im_dokument(ev.globalPosition().toPoint())
        if t == QEvent.MouseButtonPress:
            if ev.button() != Qt.LeftButton:
                self.beenden(); return True
            if pt is None:                                  # Klick außerhalb des Dokuments: beenden, Klick normal weitergeben
                self.beenden(); return False
            self.loeschen(pt)
            return True
        if t == QEvent.MouseMove:
            self._hervorheben(pt)
            return pt is not None
        return pt is not None

    def loeschen(self, pt: QPoint) -> bool:
        """Die Linie unter ``pt`` löschen (ein Rückgängig-Schritt); sonst kurze Meldung in der Statusleiste."""
        tr = self.treffer(pt)
        ok = False
        if tr is not None:
            t, (zeile, spalte, seite, _l) = tr
            c = self.ed.textCursor()
            c.beginEditBlock()
            ok = TE.linie_loeschen(t, zeile, spalte, seite)
            c.endEditBlock()
            if ok:
                self.ed.document().setModified(True)
        fenster = self.ed.window()
        if not ok and hasattr(fenster, "statusBar"):
            fenster.statusBar().showMessage("Hier gibt es keine Linie, die sich löschen lässt.", 4000)
        self._linie = None
        self.update()
        return ok

    def _hervorheben(self, pt: QPoint | None) -> None:
        tr = self.treffer(pt) if pt is not None else None
        neu = None
        if tr:
            x1, y1, x2, y2 = tr[1][3]
            (a, b), (c, d) = self._view(x1, y1), self._view(x2, y2)
            neu = (a, b, c, d)
        if neu != self._linie:
            self._linie = neu
            self.update()

    def beenden(self) -> None:
        if not getattr(self, "_aktiv", False):
            return
        self._aktiv = False
        QApplication.instance().removeEventFilter(self)
        cursor_zurueck(self)
        self.hide(); self.deleteLater()
        self.ed.setFocus()

    def paintEvent(self, _e) -> None:
        if self._linie is None:
            return
        p = QPainter(self)
        p.setPen(QPen(QColor(Farbe.ROT), 3))
        a, b, c, d = self._linie
        p.drawLine(int(a), int(b), int(c), int(d))
        p.end()
