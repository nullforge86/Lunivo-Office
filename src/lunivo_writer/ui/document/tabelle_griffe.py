"""Bedienelemente direkt an der Tabelle im Dokument (wie in WPS): Verschiebegriff oben links, „+“ rechts und unten, Aufziehgriff unten rechts
und - sobald die Tabelle über den Verschiebegriff gewählt ist - die Minisymbolleiste (``ui/widgets/mini_leiste.py``) über der Tabelle.

    TabellenGriffe(editor)       # hängt sich an den Editor; zeigt sich nur, solange die Schreibmarke in einer Tabelle steht

Alle Teile sind Kinder des Sichtbereichs und sitzen nur auf der Tabelle; das Dokument ändern allein die Befehle (``core/befehle/kontext.py``)
und die Griffe selbst über ``QTextTable`` (ein Rückgängig-Schritt je Handgriff).
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QRectF, QTimer, Qt
from PySide6.QtGui import QCursor, QIcon, QTextCursor, QTextLength
from PySide6.QtWidgets import QToolButton, QWidget

from lunivo_writer.ui.widgets import icons

GRIFF = 20
# Hell wie die übrigen Knöpfe auf dem Papier (siehe LEISTE_STIL in kopffuss_bearbeiter.py): unabhängig vom Thema des Fensters
TINTE, FLAECHE, RAND_FARBE, HOVER = "#333333", "#f5f5f5", "#c8c8c8", "#e6e6e6"
GRIFF_STIL = (f"QToolButton {{ background: {FLAECHE}; color: {TINTE}; border: 1px solid {RAND_FARBE}; border-radius: 2px; }}"
              f"QToolButton:hover {{ background: {HOVER}; }}")


def dunkel(symbol: str, px: int = 16) -> QIcon:
    """Symbol in dunkler Tinte für die hellen Knöpfe (``icons.icon`` richtet sich nach der Fensterpalette und wäre auf Hellgrau weiß)."""
    return QIcon(icons._pixmap(symbol, TINTE, max(10, px)))
RAND = 6                      # Breite des unsichtbaren Streifens über einem Spaltenrand
MIN_SPALTE = 12.0


class _Rand(QWidget):
    """Durchsichtiger Streifen über einem senkrechten Spaltenrand; Ziehen meldet die Bildpunkte seit dem Start an ``bei_ziehen``."""

    def __init__(self, vp, bei_start, bei_ziehen, bei_ende):
        super().__init__(vp)
        self.setCursor(QCursor(Qt.SizeHorCursor)); self.setFocusPolicy(Qt.NoFocus)
        self._f = (bei_start, bei_ziehen, bei_ende)
        self.spalte = 0
        self._press: QPoint | None = None

    def mousePressEvent(self, e):
        self._press = e.globalPosition().toPoint(); self._f[0](self.spalte)

    def mouseMoveEvent(self, e):
        if self._press is not None:
            self._f[1](e.globalPosition().toPoint().x() - self._press.x())

    def mouseReleaseEvent(self, e):
        if self._press is not None:
            self._press = None; self._f[2]()


class _Griff(QToolButton):
    """Ein kleiner Knopf auf dem Sichtbereich; Ziehen meldet die Mausbewegung an ``bei_ziehen`` (Bildpunkte seit dem Start)."""

    def __init__(self, vp, symbol: str, tipp: str, bei_klick=None, bei_ziehen=None, bei_ende=None, bei_start=None, cursor=None):
        super().__init__(vp)
        self.setFixedSize(GRIFF, GRIFF); self.setToolTip(tipp); self.setFocusPolicy(Qt.NoFocus); self.setAutoRaise(False)
        self.setIcon(dunkel(symbol, 14)); self.setStyleSheet(GRIFF_STIL)
        if cursor is not None:
            self.setCursor(cursor)
        self._klick, self._ziehen, self._ende, self._start = bei_klick, bei_ziehen, bei_ende, bei_start
        self._press: QPoint | None = None
        self._bewegt = False

    def mousePressEvent(self, e):
        self._press = e.globalPosition().toPoint(); self._bewegt = False
        if self._start:
            self._start()

    def mouseMoveEvent(self, e):
        if self._press is None or not self._ziehen:
            return
        d = e.globalPosition().toPoint() - self._press
        if self._bewegt or d.manhattanLength() > 4:
            self._bewegt = True
            self._ziehen(d, e.globalPosition().toPoint())

    def mouseReleaseEvent(self, e):
        gp = e.globalPosition().toPoint()
        if self._press is not None:
            if self._bewegt and self._ende:
                self._ende(gp)
            elif not self._bewegt and self._klick:
                self._klick()
        self._press = None; self._bewegt = False


class TabellenGriffe(QObject):
    def __init__(self, ed):
        super().__init__(ed)
        self.ed = ed
        vp = ed.viewport()
        self.bewegen = _Griff(vp, "move", "Tabelle markieren oder verschieben", self._waehlen, self._verschieben_zeigen, self._verschieben_ende,
                              cursor=QCursor(Qt.SizeAllCursor))
        self.spalte_plus = _Griff(vp, "plus", "Spalte am Ende einfügen", lambda: self._anhaengen(True))
        self.zeile_plus = _Griff(vp, "plus", "Zeile am Ende einfügen", lambda: self._anhaengen(False))
        self.aufziehen = _Griff(vp, "maximize-2", "Tabelle in der Größe ändern", None, self._aufziehen, self._aufziehen_ende, self._aufziehen_start,
                                cursor=QCursor(Qt.SizeFDiagCursor))
        self._raender: list[_Rand] = []
        self._rand_basis: list[float] | None = None
        self._rand_spalte = 0
        self._rand_cur: QTextCursor | None = None
        self._teile = (self.bewegen, self.spalte_plus, self.zeile_plus, self.aufziehen)
        self._basis: list[float] | None = None
        self._timer = QTimer(self); self._timer.setSingleShot(True); self._timer.setInterval(0); self._timer.timeout.connect(self.aktualisieren)
        for sig in (ed.cursorPositionChanged, ed.selectionChanged, ed.document().contentsChanged):
            sig.connect(self._timer.start)
        vp.installEventFilter(self)
        self._verstecken()

    # ---- Aufbau ----------------------------------------------------------------------------------------------------
    def eventFilter(self, obj, ev) -> bool:
        if ev.type() in (QEvent.Resize, QEvent.Paint):
            if ev.type() == QEvent.Resize:
                self._timer.start()
        return False

    # ---- Lage ------------------------------------------------------------------------------------------------------
    def tabelle(self):
        return None if self.ed.isReadOnly() else self.ed.textCursor().currentTable()

    def rechteck(self, t) -> QRectF:
        """Die Tabelle (erste Seite, wenn sie über mehrere läuft) in Bildpunkten des Sichtbereichs."""
        ed = self.ed
        r = ed.document().documentLayout().frameBoundingRect(t)
        if not ed._blatt_aktiv():
            return r
        ch = ed._sp_geo()["ch"]
        unten = min(r.bottom(), (int((r.top() + 1) // ch) + 1) * ch - 1)
        x1, y1 = ed._sp_view(r.left(), r.top()); x2, y2 = ed._sp_view(r.right(), unten)
        return QRectF(x1, y1, x2 - x1, y2 - y1)

    def _verstecken(self) -> None:
        for w in (*self._teile, *self._raender):
            w.hide()

    def aktualisieren(self) -> None:
        t = self.tabelle()
        if t is None:
                self._verstecken(); return
        r = self.rechteck(t)
        self.bewegen.move(int(r.left()) - GRIFF - 2, int(r.top()) - GRIFF - 2)
        self.spalte_plus.move(int(r.right()) + 4, int(r.center().y()) - GRIFF // 2)
        self.zeile_plus.move(int(r.center().x()) - GRIFF // 2, int(r.bottom()) + 4)
        self.aufziehen.move(int(r.right()) + 4, int(r.bottom()) + 4)
        for w in self._teile:
            w.show(); w.raise_()
        self._raender_setzen(t, r)

    # ---- Spaltenränder ---------------------------------------------------------------------------------------------
    def _grenzen(self, t) -> list[float]:
        """x-Abstand jeder Spaltengrenze (0 = linker Tabellenrand, n = rechter) vom linken Tabellenrand, in Bildpunkten."""
        doc = self.ed.document(); lay = doc.documentLayout()
        links = lay.frameBoundingRect(t).left()
        f = t.format(); n = t.columns()
        halb = f.cellPadding() + f.cellSpacing() / 2
        xs = [0.0]
        for i in range(1, n):
            blk = t.cellAt(0, i).firstCursorPosition().block()
            xs.append(lay.blockBoundingRect(blk).left() - links - halb)
        xs.append(lay.frameBoundingRect(t).width())
        return xs

    def _raender_setzen(self, t, r: QRectF) -> None:
        n = t.columns()
        while len(self._raender) < n - 1:
            self._raender.append(_Rand(self.ed.viewport(), self._rand_start, self._rand_ziehen, self._rand_ende))
        xs = self._grenzen(t)
        for i, w in enumerate(self._raender):
            if i >= n - 1:
                w.hide(); continue
            w.spalte = i
            w.setGeometry(int(r.left() + xs[i + 1]) - RAND // 2, int(r.top()), RAND, max(1, int(r.height())))
            w.show(); w.raise_()

    def _rand_start(self, spalte: int) -> None:
        t = self.tabelle()
        if t is None:
            self._rand_basis = None; return
        xs = self._grenzen(t)
        lang = t.format().columnWidthConstraints()
        if len(lang) == t.columns() and all(x.type() == QTextLength.FixedLength for x in lang):
            self._rand_basis = [x.rawValue() for x in lang]
        else:
            self._rand_basis = [xs[i + 1] - xs[i] for i in range(t.columns())]
        self._rand_spalte = spalte; self._rand_tab = t
        self._rand_cur = QTextCursor(self.ed.document()); self._rand_cur.beginEditBlock()

    def _rand_ziehen(self, dx: int) -> None:
        b = self._rand_basis
        if not b:
            return
        i = self._rand_spalte
        dx = max(MIN_SPALTE - b[i], min(b[i + 1] - MIN_SPALTE, dx))      # keine Spalte unter die Mindestbreite; Summe bleibt
        w = list(b); w[i] += dx; w[i + 1] -= dx
        f = self._rand_tab.format()
        f.setColumnWidthConstraints([QTextLength(QTextLength.FixedLength, x) for x in w])
        self._rand_tab.setFormat(f)

    def _rand_ende(self) -> None:
        if self._rand_cur is not None:
            self._rand_cur.endEditBlock(); self._rand_cur = None
        self._rand_basis = None
        self.ed.document().setModified(True)
        self.aktualisieren()

    # ---- Handgriffe ------------------------------------------------------------------------------------------------
    def _waehlen(self) -> None:
        t = self.tabelle()
        if t is None:
            return
        c = QTextCursor(self.ed.document())
        c.setPosition(t.cellAt(0, 0).firstPosition()); c.setPosition(t.cellAt(t.rows() - 1, t.columns() - 1).lastPosition(), QTextCursor.KeepAnchor)
        self.ed.setTextCursor(c); self.ed.setFocus()
        self.aktualisieren()
        hook = getattr(self.ed, "mini_hook", None)                  # die Minisymbolleiste mit Tabellenzeile über der Tabelle
        if hook is not None:
            r = self.rechteck(t)
            hook(self.ed, self.ed.viewport().mapToGlobal(QPoint(int(r.left()) + 60, int(r.top()) - GRIFF - 2)), False)

    def _anhaengen(self, spalte: bool) -> None:
        t = self.tabelle()
        if t is None:
            return
        (t.insertColumns if spalte else t.insertRows)(t.columns() if spalte else t.rows(), 1)
        self.ed.setFocus()

    def _verschieben_zeigen(self, d: QPoint, gp: QPoint) -> None:
        self.bewegen.setCursor(Qt.ClosedHandCursor)

    def _verschieben_ende(self, gp: QPoint) -> None:
        """Tabelle an die Stelle unter der Maus verschieben (vor den Absatz, auf dem losgelassen wird)."""
        self.bewegen.setCursor(Qt.SizeAllCursor)
        t = self.tabelle()
        vp = self.ed.viewport()
        if t is None:
            return
        ziel = self.ed.cursorForPosition(vp.mapFromGlobal(gp))
        if ziel.currentTable() is not None:
            return                                               # nicht in eine Tabelle hinein
        ziel.movePosition(QTextCursor.StartOfBlock)
        pos = ziel.position()
        anfang, ende = t.firstPosition() - 1, t.lastPosition() + 1
        if anfang <= pos <= ende:
            return
        quelle = QTextCursor(self.ed.document())
        quelle.setPosition(anfang); quelle.setPosition(ende, QTextCursor.KeepAnchor)
        stueck = quelle.selection()
        laenge = ende - anfang
        quelle.beginEditBlock()
        if pos > ende:
            pos -= laenge
        quelle.removeSelectedText()
        z = QTextCursor(self.ed.document()); z.setPosition(pos); z.insertFragment(stueck)
        quelle.endEditBlock()
        self.ed.document().setModified(True)

    def _aufziehen_start(self) -> None:
        t = self.tabelle()
        if t is None:
            self._basis = None; return
        r = self.rechteck(t)
        f = t.format()
        lang = f.columnWidthConstraints()
        n = t.columns()
        if len(lang) == n and all(x.type() == QTextLength.FixedLength for x in lang):
            self._basis = [x.rawValue() for x in lang]
        else:
            self._basis = [r.width() / n] * n
        self._breite0 = sum(self._basis)
        self._tab = t
        self._auf_cur = QTextCursor(self.ed.document()); self._auf_cur.beginEditBlock()

    def _aufziehen(self, d: QPoint, gp: QPoint) -> None:
        if not self._basis:
            return
        faktor = max(0.1, (self._breite0 + d.x()) / self._breite0)
        f = self._tab.format()
        f.setWidth(QTextLength())
        f.setColumnWidthConstraints([QTextLength(QTextLength.FixedLength, max(12.0, b * faktor)) for b in self._basis])
        self._tab.setFormat(f)
        self.aktualisieren()

    def _aufziehen_ende(self, gp: QPoint) -> None:
        self._basis = None
        if getattr(self, '_auf_cur', None) is not None:
            self._auf_cur.endEditBlock(); self._auf_cur = None
        self.ed.document().setModified(True)
        self.aktualisieren()
