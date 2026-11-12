"""Bedienelemente direkt an der Tabelle im Dokument (wie in gewohnten Textprogrammen): Verschiebegriff oben links, „+“ rechts und unten, Aufziehgriff unten rechts
und - sobald die Tabelle über den Verschiebegriff gewählt ist - die Minisymbolleiste (``oberflaeche/bauteile/mini_leiste.py``) über der Tabelle.

    TabellenGriffe(editor)       # hängt sich an den Editor; zeigt sich nur, solange die Schreibmarke in einer Tabelle steht

Alle Teile sind Kinder des Sichtbereichs und sitzen nur auf der Tabelle; das Dokument ändern allein die Befehle (``kern/befehle/kontextreiter/kontext.py``)
und die Griffe selbst über ``QTextTable`` (ein Rückgängig-Schritt je Handgriff).
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QCursor, QIcon, QPainter, QPen, QTextCursor, QTextLength
from PySide6.QtWidgets import QToolButton, QWidget

from lunivo_writer.editor.tabelle import tabelleneigenschaften as TE
from lunivo_writer.kern.farben import Farbe
from lunivo_writer.oberflaeche.bauteile import symbole
from lunivo_writer.oberflaeche.baukasten.basis.mass import RADIUS_LEISTENKNOPF

from lunivo_writer.oberflaeche.baukasten.basis.mass import DROPDOWN_GRIFF as GRIFF       # Seitenlänge der Griffe: eine Quelle in mass.py
# Hell wie die übrigen Knöpfe auf dem Papier (siehe LEISTE_STIL in kopffuss_bearbeiter.py): unabhängig vom Thema des Fensters
def dunkel(symbol: str, px: int = 16) -> QIcon:
    """Symbol in dunkler Tinte für die hellen Knöpfe (``icons.icon`` richtet sich nach der Fensterpalette und wäre auf Hellgrau weiß)."""
    return QIcon(symbole._pixmap(symbol, Farbe.TINTE, max(10, px)))
RAND = 6                      # Breite des unsichtbaren Streifens über einem Spaltenrand
MIN_SPALTE = 12.0


class _Vorschau(QWidget):
    """Gestrichelter Rahmen (Aufziehen) oder Linie (Rand) in der Zielgeometrie; durchsichtig für die Maus."""

    def __init__(self, vp):
        super().__init__(vp)
        self.setAttribute(Qt.WA_TransparentForMouseEvents); self.setAttribute(Qt.WA_NoSystemBackground)
        self.linie = False
        self.hide()

    def paintEvent(self, e):
        p = QPainter(self)
        pen = QPen(QColor(Farbe.AKZENT)); pen.setStyle(Qt.DashLine); pen.setWidth(1); p.setPen(pen)
        r = self.rect()
        if self.linie:
            if r.width() >= r.height():
                p.drawLine(0, r.height() // 2, r.width(), r.height() // 2)
            else:
                p.drawLine(r.width() // 2, 0, r.width() // 2, r.height())
        else:
            p.drawRect(r.adjusted(0, 0, -1, -1))


class _Grau(QWidget):
    """Graue, durchscheinende Fläche über der markierten Tabelle (Qt füllt leere Zellen einer Auswahl nicht); durchsichtig für die Maus."""

    def __init__(self, vp):
        super().__init__(vp)
        self.setAttribute(Qt.WA_TransparentForMouseEvents); self.setAttribute(Qt.WA_NoSystemBackground)
        self.hide()

    def paintEvent(self, e):
        QPainter(self).fillRect(self.rect(), QColor(128, 128, 128, 110))


class _Rand(QWidget):
    """Durchsichtiger Streifen über einem Spalten- (senkrecht) oder Zeilenrand (waagrecht); Ziehen meldet die Bildpunkte seit dem Start
    an ``bei_ziehen`` (Spalten: x, Zeilen: y)."""

    def __init__(self, vp, bei_start, bei_ziehen, bei_ende, waagrecht: bool = False):
        super().__init__(vp)
        self.setCursor(QCursor(Qt.SizeVerCursor if waagrecht else Qt.SizeHorCursor)); self.setFocusPolicy(Qt.NoFocus)
        self._f = (bei_start, bei_ziehen, bei_ende)
        self._waagrecht = waagrecht
        self.spalte = 0                                    # Index der Spalte bzw. (waagrecht) der Zeile über dem Rand
        self._press: QPoint | None = None

    def mousePressEvent(self, e):
        self._press = e.globalPosition().toPoint(); self._f[0](self.spalte)

    def mouseMoveEvent(self, e):
        if self._press is not None:
            p = e.globalPosition().toPoint()
            self._f[1](p.y() - self._press.y() if self._waagrecht else p.x() - self._press.x())

    def mouseReleaseEvent(self, e):
        if self._press is not None:
            self._press = None; self._f[2]()


class _Griff(QToolButton):
    """Ein kleiner Knopf auf dem Sichtbereich; Ziehen meldet die Mausbewegung an ``bei_ziehen`` (Bildpunkte seit dem Start)."""

    def __init__(self, vp, symbol: str, tipp: str, bei_klick=None, bei_ziehen=None, bei_ende=None, bei_start=None, cursor=None,
                 ende_immer: bool = False):
        super().__init__(vp)
        self.setFixedSize(GRIFF, GRIFF); self.setToolTip(tipp); self.setFocusPolicy(Qt.NoFocus); self.setAutoRaise(False)
        self.setIcon(dunkel(symbol, 14)); self.setProperty("papierKnopf", "griff")
        if cursor is not None:
            self.setCursor(cursor)
        self._klick, self._ziehen, self._ende, self._start = bei_klick, bei_ziehen, bei_ende, bei_start
        self._ende_immer = ende_immer          # ``bei_start`` öffnet einen Bearbeitungsblock: ``bei_ende`` schließt ihn auch ohne Ziehen
        self._press: QPoint | None = None
        self._bewegt = False
        self.unsichtbar = False                # beim Ziehen: nichts zeichnen, aber weiter sichtbar (sonst verliert er das Mausgreifen)

    def paintEvent(self, e):
        if not self.unsichtbar:
            super().paintEvent(e)

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
            elif not self._bewegt:
                if self._ende_immer and self._ende:
                    self._ende(gp, False)
                if self._klick:
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
                                cursor=QCursor(Qt.SizeFDiagCursor), ende_immer=True)
        self._raender: list[_Rand] = []
        self._rand_basis: list[float] | None = None
        self._rand_spalte = 0
        self._zraender: list[_Rand] = []                    # waagrechte Streifen über den Zeilenrändern
        self._zeile_nr = 0
        self._zeile_h0 = 0.0
        self._teile = (self.bewegen, self.spalte_plus, self.zeile_plus, self.aufziehen)
        self._basis: list[float] | None = None
        self._halter: QWidget | None = None        # das gerade gezogene Teil: bleibt (unsichtbar) bestehen und behält die Maus
        self._v_aktiv = False                      # Verschiebegriff wird gezogen
        self._ziehen = False                       # Ziehvorgang offen: ``aktualisieren`` ruht
        self._offen = False                        # Aufziehen oder Rand wird gezogen: die Tabelle bleibt unverändert, nur die Vorschau folgt der Maus
        self._anwenden = None                      # Änderung für das Loslassen (nur die letzte Mausposition zählt)
        self._vorschau = _Vorschau(vp)
        self._grau = _Grau(vp)
        self._timer = QTimer(self); self._timer.setSingleShot(True); self._timer.setInterval(0); self._timer.timeout.connect(self.aktualisieren)
        for sig in (ed.cursorPositionChanged, ed.selectionChanged, ed.document().contentsChanged):
            sig.connect(self._timer.start)
        if hasattr(ed, "leseschutzGeaendert"):
            ed.leseschutzGeaendert.connect(lambda _ro: self.aktualisieren())      # Nur-Lesen: Griffe sofort aus- bzw. einblenden
        vp.installEventFilter(self)
        ed.installEventFilter(self)             # Esc und Fokusverlust schließen einen offenen Ziehvorgang
        self._verstecken()

    # ---- Aufbau ----------------------------------------------------------------------------------------------------
    def eventFilter(self, obj, ev) -> bool:
        if obj is self.ed:
            if ev.type() == QEvent.FocusOut or (ev.type() == QEvent.KeyPress and ev.key() == Qt.Key_Escape):
                self._bloecke_schliessen()
            return False
        if ev.type() == QEvent.Resize:
            self._timer.start()
        return False

    def _bloecke_schliessen(self) -> None:
        """Offene Ziehvorgänge (Esc, Fokusverlust) ohne Änderung verwerfen."""
        if self._offen:
            self._ziehen_ende(False)
        if self._v_aktiv:
            self._verschieben_frei()
        for w in self._teile:
            w._press = None
        for w in (*self._raender, *self._zraender):
            w._press = None

    # ---- Lage ------------------------------------------------------------------------------------------------------
    def tabelle(self):
        return None if self.ed.isReadOnly() else self.ed.textCursor().currentTable()

    def _gezeichnet(self, t) -> QRectF:
        """Der wirklich gezeichnete Rahmen in Layoutkoordinaten: aus den Zellen (Inhalt plus Innenabstand), nicht aus ``frameBoundingRect``
        (das liegt um Rahmen-/Randmaße daneben und wandert bei erhöhtem oberem Innenabstand der Zeilenhöhe)."""
        lay = self.ed.document().documentLayout()
        f = t.format(); pad = f.cellPadding()
        def rand(z, name):
            v = getattr(z.format().toTableCellFormat(), name)()
            return v if v > 0 else pad
        a = t.cellAt(0, 0); b = t.cellAt(0, t.columns() - 1)
        links = lay.blockBoundingRect(a.firstCursorPosition().block()).left() - rand(a, "leftPadding")
        rechts = lay.blockBoundingRect(b.firstCursorPosition().block()).right() + rand(b, "rightPadding")
        oben = TE._zeilen_oberkanten(t)[0]
        return QRectF(links, oben, rechts - links, max(1.0, TE._unterkante(t) - oben))

    def rechteck(self, t) -> QRectF:
        """Die Tabelle (erste Seite, wenn sie über mehrere läuft) in Bildpunkten des Sichtbereichs."""
        ed = self.ed
        r = self._gezeichnet(t)
        if not ed._blatt_aktiv():
            return r
        ch = ed._sp_geo()["ch"]
        unten = min(r.bottom(), (int((r.top() + 1) // ch) + 1) * ch - 1)
        x1, y1 = ed._sp_view(r.left(), r.top()); x2, y2 = ed._sp_view(r.right(), unten)
        return QRectF(x1, y1, x2 - x1, y2 - y1)

    def _verstecken(self) -> None:
        self._bloecke_schliessen()
        for w in (*self._teile, *self._raender, *self._zraender):
            w.hide()

    def aktualisieren(self) -> None:
        if self._ziehen:
            return
        t = self.tabelle()
        if t is None:
                self._verstecken(); return
        r = self.rechteck(t)
        self._griffe_setzen(r)
        for w in self._teile:
            w.show(); w.raise_()
        self._raender_setzen(t, r)
        self._zeilenraender_setzen(t, r)

    # ---- Ziehen: Tabelle bleibt unverändert, Vorschau zeigt das Ziel, geändert wird beim Loslassen -------------------
    def _ausblenden(self, halter: QWidget) -> None:
        """Alle Tabellensymbole außer dem gezogenen verstecken; dieses bleibt sichtbar, zeichnet aber nichts (behält die Maus)."""
        self._halter = halter
        for w in (*self._teile, *self._raender, *self._zraender):
            if w is not halter:
                w.hide()
        if isinstance(halter, _Griff):
            halter.unsichtbar = True; halter.update()

    def _einblenden(self) -> None:
        h, self._halter = self._halter, None
        if isinstance(h, _Griff):
            h.unsichtbar = False; h.update()

    def _ziehen_start(self, t, halter: QWidget) -> None:
        """Merkt Rechteck und Zoom beim Start; ab jetzt ruht ``aktualisieren`` (auch das Absatz-Symbol)."""
        self._ausblenden(halter)
        self._ziehen = self._offen = True; self._anwenden = None; self._timer.stop()
        self._z_r0 = self.rechteck(t)
        self._z_zoom = TE._zoom(t)
        ap = getattr(self.ed, "_absatz_symbol", None)
        if ap is not None:
            ap.pausiert = True

    def _ziehen_ende(self, anwenden: bool = True) -> None:
        """Loslassen (``anwenden``) oder Verwerfen: die vorgemerkte Änderung genau einmal und als ein Rückgängig-Schritt ausführen."""
        if not self._offen:
            return
        self._offen = False; self._vorschau.hide(); self._grau.hide()
        fn, self._anwenden = self._anwenden, None
        if fn is not None and anwenden:
            c = QTextCursor(self.ed.document()); c.beginEditBlock()
            try:
                fn()
            finally:
                c.endEditBlock()
        self._ziehen_frei(fn is not None and anwenden)

    def _ziehen_frei(self, geaendert: bool) -> None:
        """Ruhe aufheben und einmal vollständig aktualisieren."""
        self._ziehen = False; self._timer.stop(); self._einblenden()
        ap = getattr(self.ed, "_absatz_symbol", None)
        if ap is not None:
            ap.pausiert = False
            ap.aktualisieren()
        if geaendert:
            self.ed.document().setModified(True)
        self.aktualisieren()                       # Symbole erscheinen wieder und rasten am neuen Rand ein

    def _markieren(self) -> None:
        """Die ganze Tabelle grau zeigen (wie in gewohnten Textprogrammen beim Aufziehen); die Textauswahl bleibt unberührt, ``_ziehen_ende`` blendet die Fläche aus."""
        self._grau.setGeometry(self._z_r0.toAlignedRect()); self._grau.show(); self._grau.raise_()

    def _auswahl_alle(self, t) -> None:
        c = QTextCursor(self.ed.document())
        c.setPosition(t.cellAt(0, 0).firstPosition()); c.setPosition(t.cellAt(t.rows() - 1, t.columns() - 1).lastPosition(), QTextCursor.KeepAnchor)
        self.ed.setTextCursor(c)

    def _griffe_setzen(self, r: QRectF) -> None:
        self.bewegen.move(int(r.left()) - GRIFF - 2, int(r.top()) - GRIFF - 2)
        self.spalte_plus.move(int(r.right()) + 4, int(r.center().y()) - GRIFF // 2)
        self.zeile_plus.move(int(r.center().x()) - GRIFF // 2, int(r.bottom()) + 4)
        self.aufziehen.move(int(r.right()) + 4, int(r.bottom()) + 4)

    def _vorschau_zeigen(self, geo: QRect, linie: bool) -> None:
        v = self._vorschau
        v.linie = linie; v.setGeometry(geo); v.show(); v.raise_(); v.update()

    # ---- Spaltenränder ---------------------------------------------------------------------------------------------
    def _grenzen(self, t) -> list[float]:
        """x-Abstand jeder Spaltengrenze (0 = linker Tabellenrand, n = rechter) vom linken Tabellenrand, in Bildpunkten."""
        doc = self.ed.document(); lay = doc.documentLayout()
        gz = self._gezeichnet(t); links = gz.left()
        f = t.format(); n = t.columns()
        halb = f.cellPadding() + f.cellSpacing() / 2
        xs = [0.0]
        for i in range(1, n):
            blk = t.cellAt(0, i).firstCursorPosition().block()
            xs.append(lay.blockBoundingRect(blk).left() - links - halb)
        xs.append(gz.width())
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
        self._rand_spalte = spalte; self._rand_tab = t; self._rand_x0 = xs[spalte + 1]
        self._ziehen_start(t, self._raender[spalte] if spalte < len(self._raender) else None)

    def _rand_ziehen(self, dx: int) -> None:
        b = self._rand_basis
        if not b or not self._offen:
            return
        i = self._rand_spalte; z = self._z_zoom
        dd = dx / z                                                         # Bildpunkte → Dokumentmaß
        dd = max(MIN_SPALTE - b[i], min(b[i + 1] - MIN_SPALTE, dd))        # keine Spalte unter die Mindestbreite; Summe bleibt
        r = self._z_r0
        self._vorschau_zeigen(QRect(int(r.left() + self._rand_x0 + dd * z) - 1, int(r.top()), 3, max(1, int(r.height()))), True)
        w = list(b); w[i] += dd; w[i + 1] -= dd
        self._anwenden = lambda: self._spalten_anwenden(w)

    def _spalten_anwenden(self, w: list[float]) -> None:
        f = self._rand_tab.format()
        f.setColumnWidthConstraints([QTextLength(QTextLength.FixedLength, x) for x in w])
        self._rand_tab.setFormat(f)

    def _rand_ende(self, geaendert: bool = True) -> None:
        self._rand_basis = None
        self._ziehen_ende(geaendert)

    # ---- Zeilenränder ----------------------------------------------------------------------------------------------
    def _zeilenraender_setzen(self, t, r: QRectF) -> None:
        n = t.rows()
        while len(self._zraender) < n - 1:
            self._zraender.append(_Rand(self.ed.viewport(), self._zeile_start, self._zeile_ziehen, self._zeile_ende, waagrecht=True))
        ys = TE.zeilengrenzen(t)
        oben = self._gezeichnet(t).top()
        for i, w in enumerate(self._zraender):
            if i >= n - 1 or i >= len(ys):
                w.hide(); continue
            y = r.top() + (ys[i] - oben)
            if y > r.bottom():                                       # Zeilen auf einer späteren Seite: kein Streifen
                w.hide(); continue
            w.spalte = i
            w.setGeometry(int(r.left()), int(y) - RAND // 2, max(1, int(r.width())), RAND)
            w.show(); w.raise_()

    def _zeile_start(self, zeile: int) -> None:
        t = self.tabelle()
        if t is None:
            return
        self._zeile_tab, self._zeile_nr = t, zeile
        self._zeile_h0 = TE.tabelle_basis(t)[1][zeile]               # Dokumentmaß (Layout / Zoom)
        self._zeile_min = TE.zeilen_mindesthoehe(t, zeile)
        self._zeile_y0 = TE.zeilengrenzen(t)[zeile] - self._gezeichnet(t).top()
        self._ziehen_start(t, self._zraender[zeile] if zeile < len(self._zraender) else None)

    def _zeile_ziehen(self, dy: int) -> None:
        if not self._offen:
            return
        z = self._z_zoom
        h = max(self._zeile_min, self._zeile_h0 + dy / z)               # Bildpunkte → Dokumentmaß, nie unter dem Inhalt
        r = self._z_r0
        self._vorschau_zeigen(QRect(int(r.left()), int(r.top() + self._zeile_y0 + (h - self._zeile_h0) * z) - 1, max(1, int(r.width())), 3), True)
        tab, nr = self._zeile_tab, self._zeile_nr
        self._anwenden = lambda: TE.zeile_hoehe_ziehen(tab, nr, h)

    def _zeile_ende(self, geaendert: bool = True) -> None:
        self._ziehen_ende(geaendert)

    # ---- Handgriffe ------------------------------------------------------------------------------------------------
    def _waehlen(self) -> None:
        t = self.tabelle()
        if t is None:
            return
        self._auswahl_alle(t); self.ed.setFocus()
        self.aktualisieren()
        hook = getattr(self.ed, "mini_hook", None)                  # die Minisymbolleiste mit Tabellenzeile über der Tabelle
        if hook is not None:
            r = self.rechteck(t)
            self.ed.mini_per_griff = True                            # die Leiste zeigt Tabellenfunktionen (auch bei einer Tabelle mit einer Zelle)
            hook(self.ed, self.ed.viewport().mapToGlobal(QPoint(int(r.left()) + 60, int(r.top()) - GRIFF - 2)), False)

    def _anhaengen(self, spalte: bool) -> None:
        """Symbole kurz ausblenden, Spalte/Zeile anhängen, nach dem Layout am neuen Rand wieder einblenden (kein zweiter Klick dazwischen)."""
        t = self.tabelle()
        if t is None or self._ziehen:
            return
        self._ausblenden(None); self._ziehen = True; self._timer.stop()
        (t.insertColumns if spalte else t.insertRows)(t.columns() if spalte else t.rows(), 1)
        self.ed.setFocus()
        QTimer.singleShot(0, lambda: self._ziehen_frei(True))

    def _verschieben_zeigen(self, d: QPoint, gp: QPoint) -> None:
        self.bewegen.setCursor(Qt.ClosedHandCursor)
        if not self._v_aktiv and not self._ziehen:
            self._v_aktiv = True; self._ziehen = True; self._timer.stop()
            self._ausblenden(self.bewegen)
            ap = getattr(self.ed, "_absatz_symbol", None)
            if ap is not None:
                ap.pausiert = True

    def _verschieben_frei(self) -> None:
        self._v_aktiv = False; self._ziehen_frei(False)

    def _verschieben_ende(self, gp: QPoint) -> None:
        """Tabelle an die Stelle unter der Maus verschieben (vor den Absatz, auf dem losgelassen wird)."""
        try:
            self._verschieben_ende_tun(gp)
        finally:
            if self._v_aktiv:
                self._verschieben_frei()

    def _verschieben_ende_tun(self, gp: QPoint) -> None:
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
        self._basis = TE.tabelle_basis(t)                               # (Spaltenbreiten, Zeilenhöhen) im Dokumentmaß
        self._tab = t
        self._ziehen_start(t, self.aufziehen)
        r = self._z_r0
        self._ansicht0 = (max(1.0, r.width()), max(1.0, r.height()))     # Größe auf dem Bildschirm: der Mausweg bezieht sich darauf
        self._auf_min = [TE.zeilen_mindesthoehe(t, k) for k in range(t.rows())]

    def _aufziehen(self, d: QPoint, gp: QPoint) -> None:
        """Nur der gestrichelte Rahmen von der oberen linken Ecke bis zum Ziel; die Tabelle bleibt (grau markiert) unverändert."""
        if not self._basis or not self._offen:
            return
        if not self._grau.isVisible():
            self._markieren()
        w0, h0 = self._ansicht0
        fb = max(0.1, (w0 + d.x()) / w0)
        fh = max(0.1, (h0 + d.y()) / h0)
        z, (bb, bh) = self._z_zoom, self._basis
        # Zielgröße wie ``tabelle_skalieren``: Spalten mindestens ``MIN_SPALTE``, Zeilen mindestens Inhalt
        dw = sum((max(TE.MIN_SPALTE, b * fb) - b) * z for b in bb)
        dh = sum((max(self._auf_min[k] if k < len(self._auf_min) else 1.0, h * fh) - h) * z for k, h in enumerate(bh))
        r0 = self._z_r0
        self._vorschau_zeigen(QRectF(r0.left(), r0.top(), max(1.0, r0.width() + dw), max(1.0, r0.height() + dh)).toAlignedRect(), False)
        tab, b0, h0l = self._tab, bb, bh
        self._anwenden = lambda: TE.tabelle_skalieren(tab, b0, h0l, fb, fh)

    def _aufziehen_ende(self, gp: QPoint | None, geaendert: bool = True) -> None:
        """Loslassen: einmal skalieren (auch bei Klick ohne Ziehen wird der Vorgang geschlossen)."""
        self._basis = None
        self._ziehen_ende(geaendert)
