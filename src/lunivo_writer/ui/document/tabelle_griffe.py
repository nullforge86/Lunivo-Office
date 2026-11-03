"""Bedienelemente direkt an der Tabelle im Dokument (wie in WPS): Verschiebegriff oben links, „+“ rechts und unten, Aufziehgriff unten rechts
und eine kleine Leiste („Einfügen“, „Löschen“, „Eigenschaften“) über der Tabelle, sobald die Tabelle gewählt ist.

    TabellenGriffe(editor)       # hängt sich an den Editor; zeigt sich nur, solange die Schreibmarke in einer Tabelle steht

Alle Teile sind Kinder des Sichtbereichs und sitzen nur auf der Tabelle; das Dokument ändern allein die Befehle (``core/befehle/kontext.py``)
und die Griffe selbst über ``QTextTable`` (ein Rückgängig-Schritt je Handgriff).
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QRectF, QTimer, Qt
from PySide6.QtGui import QCursor, QTextCursor, QTextLength
from PySide6.QtWidgets import QFrame, QHBoxLayout, QMenu, QToolButton, QWidget

from lunivo_writer.ui.widgets import icons

GRIFF = 20


class _Griff(QToolButton):
    """Ein kleiner Knopf auf dem Sichtbereich; Ziehen meldet die Mausbewegung an ``bei_ziehen`` (Bildpunkte seit dem Start)."""

    def __init__(self, vp, symbol: str, tipp: str, bei_klick=None, bei_ziehen=None, bei_ende=None, bei_start=None, cursor=None):
        super().__init__(vp)
        self.setFixedSize(GRIFF, GRIFF); self.setToolTip(tipp); self.setFocusPolicy(Qt.NoFocus); self.setAutoRaise(False)
        self.setIcon(icons.icon(symbol, 14)); self.setStyleSheet("QToolButton { background: palette(base); border: 1px solid palette(mid); border-radius: 3px; }"
                                                              "QToolButton:hover { background: palette(midlight); }")
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
        self.leiste = self._leiste(vp)
        self._teile = (self.bewegen, self.spalte_plus, self.zeile_plus, self.aufziehen)
        self._basis: list[float] | None = None
        self._tabelle_gewaehlt = False
        self._timer = QTimer(self); self._timer.setSingleShot(True); self._timer.setInterval(0); self._timer.timeout.connect(self.aktualisieren)
        for sig in (ed.cursorPositionChanged, ed.selectionChanged, ed.document().contentsChanged):
            sig.connect(self._timer.start)
        vp.installEventFilter(self)
        self._verstecken()

    # ---- Aufbau ----------------------------------------------------------------------------------------------------
    def _leiste(self, vp) -> QWidget:
        f = QFrame(vp); f.setFrameShape(QFrame.StyledPanel); f.setAutoFillBackground(True)
        h = QHBoxLayout(f); h.setContentsMargins(4, 2, 4, 2); h.setSpacing(2)
        self._menue_knoepfe = []
        for text, namen in (("Einfügen", (("Zeile oberhalb", "tabelleZeileOben"), ("Zeile unterhalb", "tabelleZeileUnten"),
                                          ("Spalte links", "tabelleSpalteLinks"), ("Spalte rechts", "tabelleSpalteRechts"))),
                            ("Löschen", (("Zeile", "tabelleZeileLoeschen"), ("Spalte", "tabelleSpalteLoeschen"), ("Tabelle", "tabelleLoeschen")))):
            b = QToolButton(f); b.setText(text); b.setPopupMode(QToolButton.InstantPopup); b.setFocusPolicy(Qt.NoFocus); b.setAutoRaise(True)
            m = QMenu(b)
            for name, befehl in namen:
                m.addAction(name, lambda _=False, bf=befehl: self._befehl(bf))
            b.setMenu(m); h.addWidget(b)
        for symbol, tipp, befehl in (("bold", "Fett", "fett"), ("links", "Links im Feld", "zelleLinks"),
                                     ("mitte", "Zentriert im Feld", "zelleZentriert"), ("rechts", "Rechts im Feld", "zelleRechts")):
            b = QToolButton(f); b.setIcon(icons.icon(symbol, 16)); b.setToolTip(tipp); b.setAutoRaise(True); b.setFocusPolicy(Qt.NoFocus)
            b.setFixedSize(28, 24); b.clicked.connect(lambda _=False, bf=befehl: self._befehl(bf)); h.addWidget(b)
        e = QToolButton(f); e.setText("Eigenschaften …"); e.setAutoRaise(True); e.setFocusPolicy(Qt.NoFocus)
        e.clicked.connect(lambda: self._befehl("tabelleEigenschaften")); h.addWidget(e)
        return f

    def _befehl(self, name: str) -> None:
        w = self.ed.window()
        getattr(w.befehle, name)()
        self._timer.start()

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
        for w in (*self._teile, self.leiste):
            w.hide()

    def aktualisieren(self) -> None:
        t = self.tabelle()
        if t is None:
            self._tabelle_gewaehlt = False
            self._verstecken(); return
        r = self.rechteck(t)
        vp = self.ed.viewport().rect()
        self.bewegen.move(int(r.left()) - GRIFF - 2, int(r.top()) - GRIFF - 2)
        self.spalte_plus.move(int(r.right()) + 4, int(r.center().y()) - GRIFF // 2)
        self.zeile_plus.move(int(r.center().x()) - GRIFF // 2, int(r.bottom()) + 4)
        self.aufziehen.move(int(r.right()) + 4, int(r.bottom()) + 4)
        for w in self._teile:
            w.show(); w.raise_()
        c = self.ed.textCursor()
        gewaehlt = c.hasSelection() and (self._tabelle_gewaehlt or t.cellAt(c.selectionStart()) != t.cellAt(c.selectionEnd()))
        if gewaehlt:
            self.leiste.adjustSize()
            x = min(int(r.left()), vp.width() - self.leiste.width())      # nicht über den Sichtbereich hinausragen
            self.leiste.move(max(0, x), max(0, int(r.top()) - GRIFF - self.leiste.height() - 6)); self.leiste.show(); self.leiste.raise_()
        else:
            self.leiste.hide()

    # ---- Handgriffe ------------------------------------------------------------------------------------------------
    def _waehlen(self) -> None:
        t = self.tabelle()
        if t is None:
            return
        c = QTextCursor(self.ed.document())
        c.setPosition(t.cellAt(0, 0).firstPosition()); c.setPosition(t.cellAt(t.rows() - 1, t.columns() - 1).lastPosition(), QTextCursor.KeepAnchor)
        self._tabelle_gewaehlt = True
        self.ed.setTextCursor(c); self.ed.setFocus()
        self.aktualisieren()

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
        t.document() and QTextCursor(self.ed.document()).beginEditBlock()

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
        self.ed.document().setModified(True)
        self.aktualisieren()
