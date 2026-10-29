"""Kopf- und Fußzeile direkt auf der Seite bearbeiten (Einfügen ▸ Kopf- und Fußzeile, Doppelklick in den Seitenrand).

    b = editor.kopffuss()                 # der Bearbeiter des Editors (wird beim ersten Aufruf angelegt)
    b.starte("kopf")                      # oder "fuss"; ``b.aktiv``, ``b.beende()``, ``b.wechseln()``, ``b.abschnitt_springen(+1)``

Gespeichert wird weiter in ``PageSettings.header`` / ``footer`` (Text mit {PAGE}); die Seite wird nicht anders gezeichnet. Über dem Kopf-
bereich des Blattes liegt ein randloses Textfeld (gestrichelter Rahmen), darunter die schwebende Leiste mit „Kopfzeile“, „Seitenzahl neu
aufbauen“, „Seitenzahlenformat“ und „Seitenzahl löschen“, links das Absatz-Symbol. Esc oder Doppelklick in den Text beenden. Kein HTML."""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QPlainTextEdit, QToolButton, QWidget, QWidgetAction

from lunivo_writer.editor import seitenzahl as SZ
from lunivo_writer.models.page import HeaderFooter, mm_to_px
from lunivo_writer.ui.baukasten.menue_liste import MenueListe

_FLAG = {"left": Qt.AlignLeft, "center": Qt.AlignHCenter, "right": Qt.AlignRight}
FORMATE = [("dezimal", "1, 2, 3 …"), ("klein", "a, b, c …"), ("gross", "A, B, C …"), ("roem_klein", "i, ii, iii …"), ("roem_gross", "I, II, III …")]


class _Feld(QPlainTextEdit):
    """Das Textfeld über dem Kopfbereich: randlos, gestrichelter Rahmen, Esc beendet."""
    schliessen = Signal()

    def __init__(self, eltern):
        super().__init__(eltern)
        self.setFrameShape(QPlainTextEdit.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAccessibleName("Kopf- und Fußzeile")
        self.setPlaceholderText("{PAGE} = Seitenzahl, {PAGES} = Seitenanzahl")

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.schliessen.emit()
            return
        super().keyPressEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        p = QPainter(self.viewport())
        pen = QPen(QColor("#8a8a8a")); pen.setStyle(Qt.DashLine); pen.setWidth(1)
        p.setPen(pen)
        p.drawRect(self.viewport().rect().adjusted(0, 0, -1, -1))


class _Leiste(QWidget):
    """Die schwebende Leiste: Etikett und drei Knöpfe mit Auswahl."""

    def __init__(self, eltern):
        super().__init__(eltern)
        h = QHBoxLayout(self); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(4)
        self.etikett = QLabel("Kopfzeile"); self.etikett.setContentsMargins(6, 2, 6, 2)
        h.addWidget(self.etikett)
        self.knopf = {}
        for schl, text in (("neu", "Seitenzahl neu aufbauen"), ("format", "Seitenzahlenformat"), ("loeschen", "Seitenzahl löschen")):
            k = QToolButton(); k.setText(text); k.setPopupMode(QToolButton.InstantPopup); k.setAutoRaise(True)
            h.addWidget(k); self.knopf[schl] = k
        self.adjustSize()


class KopfFussBearbeiter(QObject):
    gestartet = Signal(); beendet = Signal()

    def __init__(self, editor):
        super().__init__(editor)
        self.ed = editor
        self.aktiv = False
        self.zone = "kopf"
        self.blatt = 0
        self.feld = self.leiste = self.absatz = None
        self._laedt = False
        self._zeit = QTimer(self); self._zeit.setSingleShot(True); self._zeit.setInterval(200); self._zeit.timeout.connect(self.speichern)

    # ---- Start und Ende ------------------------------------------------------------------------------------------
    def starte(self, zone: str = "kopf", blatt: int | None = None) -> bool:
        ed = self.ed
        if ed.web:
            return False
        if self.aktiv:
            self.speichern()
        self.zone = "fuss" if zone == "fuss" else "kopf"
        self.blatt = self._cursor_blatt() if blatt is None else blatt
        if self.feld is None:
            vp = ed.viewport()
            self.feld = _Feld(vp); self.feld.schliessen.connect(self.beende)
            self.feld.textChanged.connect(self._geaendert)
            self.leiste = _Leiste(vp)
            self.absatz = QToolButton(vp); self.absatz.setText("¶"); self.absatz.setAutoRaise(True)
            self.absatz.setPopupMode(QToolButton.InstantPopup); self.absatz.setToolTip("Absatz")
            vp.installEventFilter(self)
            self._menues()
        self.aktiv = True
        self._laden()
        self._platzieren()
        for w in (self.feld, self.leiste, self.absatz):
            w.show(); w.raise_()
        self.feld.setFocus()
        self.gestartet.emit()
        return True

    def beende(self) -> None:
        if not self.aktiv:
            return
        self.speichern()
        self.aktiv = False
        for w in (self.feld, self.leiste, self.absatz):
            if w is not None:
                w.hide()
        self.ed.viewport().update()
        self.ed.setFocus()
        self.beendet.emit()

    def wechseln(self) -> None:
        if self.aktiv:
            self.starte("fuss" if self.zone == "kopf" else "kopf", self.blatt)

    def abschnitt_springen(self, schritt: int) -> bool:
        """Zur Kopfzeile des vorigen/nächsten Abschnitts; → False, wenn es keinen gibt."""
        from lunivo_writer.editor import abschnitte as AB
        ed = self.ed
        ziel = ed.abschnitt_nr() + schritt
        if ziel < 0 or ziel >= AB.anzahl(ed.document()):
            return False
        self.speichern()
        c = ed.textCursor(); c.setPosition(AB.beginn(ed.document(), ziel)); ed.setTextCursor(c)
        if self.aktiv:
            self.starte(self.zone)
        return True

    # ---- Seite und Text --------------------------------------------------------------------------------------------
    def _cursor_blatt(self) -> int:
        ed = self.ed
        try:
            y = ed.cursorRect().center().y()
            return max(0, int(ed._blatt_bei_y(y)))
        except Exception:
            return 0

    def _name(self, page) -> str:
        erste = self.blatt == 0 and page.diff_first
        return ("first_" if erste else "") + ("header" if self.zone == "kopf" else "footer")

    def hf(self, page=None) -> HeaderFooter:
        page = page or self.ed.abschnitt_seite()
        return getattr(page, self._name(page))

    def _laden(self) -> None:
        page = self.ed.abschnitt_seite()
        hf = self.hf(page)
        self._laedt = True
        self.feld.setPlainText(hf.text)
        self._laedt = False
        self._ausrichten(hf.align)
        self.leiste.etikett.setText("Kopfzeile" if self.zone == "kopf" else "Fußzeile")
        self.leiste.etikett.setAccessibleName(self.leiste.etikett.text())

    def _ausrichten(self, align: str) -> None:
        al = _FLAG.get(SZ.ausrichtung(align, self.blatt + 1), Qt.AlignLeft)
        o = self.feld.document().defaultTextOption(); o.setAlignment(al | Qt.AlignVCenter)
        self.feld.document().setDefaultTextOption(o)
        c = self.feld.textCursor(); c.select(c.SelectionType.Document)
        bf = c.blockFormat(); bf.setAlignment(al); c.setBlockFormat(bf)

    def _geaendert(self) -> None:
        if not self._laedt and self.aktiv:
            self._zeit.start()

    def speichern(self) -> None:
        """Den Text des Feldes in die Seiteneinrichtung des Abschnitts schreiben (sofort; sonst nach kurzer Pause beim Tippen)."""
        self._zeit.stop()
        if not self.aktiv or self.feld is None:
            return
        page = self.ed.abschnitt_seite()
        hf = self.hf(page)
        text = self.feld.toPlainText().strip("\n")
        if text == hf.text:
            return
        setattr(page, self._name(page), HeaderFooter(text, hf.align))
        self.ed.page_settings_changed(page)

    def aendern(self, aendere, neu_laden: bool = True) -> None:
        """``aendere(page)`` auf die Einrichtung des aktuellen Abschnitts anwenden und speichern; → danach das Feld neu füllen."""
        self.speichern()
        page = self.ed.abschnitt_seite()
        if aendere(page) is False:
            return
        self.ed.page_settings_changed(page)
        if self.aktiv and neu_laden:
            self._laden()
            self._platzieren()

    def ausrichtung_setzen(self, align: str) -> None:
        def f(page):
            hf = self.hf(page)
            setattr(page, self._name(page), HeaderFooter(hf.text, align))
        self.aendern(f)

    def tabstopp_einfuegen(self) -> None:
        if self.aktiv:
            self.feld.insertPlainText("\t"); self.feld.setFocus()

    # ---- Lage ----------------------------------------------------------------------------------------------------
    def _rect(self) -> QRectF:
        ed = self.ed
        z = ed.zoom
        b = ed._blatt(self.blatt)
        oben = ed.blatt_oben(self.blatt)
        h = mm_to_px(10) * z
        y = oben + mm_to_px(8) * z if self.zone == "kopf" else oben + b["H"] - mm_to_px(18) * z
        return QRectF(b["x"] + b["ml"], y, b["cw"], h)

    def _platzieren(self) -> None:
        if not self.aktiv:
            return
        r = self._rect()
        g = r.toRect()
        if self.feld.geometry() != g:
            self.feld.setGeometry(g)
        f = QFont(self.ed.font()); f.setPixelSize(max(6, round(13 * self.ed.zoom)))
        if self.feld.font() != f:
            self.feld.setFont(f)
        self.leiste.adjustSize()
        ly = g.bottom() + 3 if self.zone == "kopf" else g.top() - self.leiste.height() - 3
        self.leiste.move(g.left(), max(0, ly))
        self.absatz.adjustSize()
        self.absatz.move(max(0, g.left() - self.absatz.width() - 4), g.top())

    def eventFilter(self, o, e):
        try:
            if self.aktiv and o is self.ed.viewport() and e.type() in (QEvent.Resize, QEvent.Paint):
                self._platzieren()
        except RuntimeError:                                    # Editor beim Beenden schon abgebaut
            pass
        return False

    # ---- Menüs -------------------------------------------------------------------------------------------------------
    def _menues(self) -> None:
        k = self.leiste.knopf
        m = MenueListe(self.leiste); k["neu"].setMenu(m); m.aboutToShow.connect(lambda m=m: self._menue_neu(m))
        m = MenueListe(self.leiste); k["format"].setMenu(m); m.aboutToShow.connect(lambda m=m: self._menue_format(m))
        m = MenueListe(self.leiste); k["loeschen"].setMenu(m); m.aboutToShow.connect(lambda m=m: self._menue_loeschen(m))
        m = MenueListe(self.absatz); self.absatz.setMenu(m)
        m.eintrag("Absatzformat zurücksetzen", lambda: self.ausrichtung_setzen("center"))
        m.eintrag("Symbol vom Absatz-Layout ausblenden", self.absatz.hide)

    def _menue_neu(self, m: MenueListe) -> None:
        m.clear()
        page = self.ed.abschnitt_seite()
        sp = QDoubleSpinBox(); sp.setDecimals(0); sp.setRange(1, 99999); sp.setValue(SZ.erste_nummer(page)); sp.setPrefix("Seitennummerierung: ")
        sp.setAccessibleName("Seitennummerierung")
        sp.editingFinished.connect(lambda: self._start_setzen(int(sp.value())))
        a = QWidgetAction(m); a.setDefaultWidget(sp); m.addAction(a)
        m.eintrag("Nummerierung fortsetzen", lambda: self._start_setzen(0), aktiv=page.seiten_start > 0)

    def _start_setzen(self, n: int) -> None:
        self.aendern(lambda p: setattr(p, "seiten_start", max(0, n)))

    def _menue_format(self, m: MenueListe) -> None:
        m.clear()
        aktuell = self.ed.abschnitt_seite().seiten_format
        for schl, text in FORMATE:
            m.eintrag(text, lambda s=schl: self.aendern(lambda p: setattr(p, "seiten_format", s)), haken=schl == aktuell)

    def _menue_loeschen(self, m: MenueListe) -> None:
        m.clear()
        m.eintrag("Aktuelle Seite", lambda: self.seitenzahl_loeschen("aktuelle"))
        m.eintrag("Gesamtes Dokument", lambda: self.seitenzahl_loeschen("dokument"))
        m.eintrag("Auf aktuelle Seite", lambda: self.seitenzahl_loeschen("auf"))
        m.eintrag("Von aktueller Seite", lambda: self.seitenzahl_loeschen("von"))
        m.eintrag("Aktueller Abschnitt", lambda: self.seitenzahl_loeschen("abschnitt"))

    def seitenzahl_loeschen(self, art: str) -> bool | None:
        """Seitenzahl entfernen: "dokument" (alle Abschnitte), "abschnitt", "aktuelle", "auf", "von" (siehe ``seitenzahl_loeschen_bereich``).
        → True/False: geändert/gab keine, None: nicht darstellbar (Hinweis in der Statusleiste)."""
        from lunivo_writer.editor import abschnitte as AB
        self.speichern()
        ed = self.ed
        if art == "dokument":
            gab = False
            for nr in range(AB.anzahl(ed.document())):
                pg = ed.abschnitt_seite(nr)
                if SZ.seitenzahlen_entfernen(pg):
                    gab = True
                    if nr > 0:
                        AB.setzen(ed.document(), nr, pg)
                    else:
                        ed.apply_page(pg)
            ed._recount(); ed.viewport().update(); ed.document().setModified(True)
            ergebnis = gab
        else:
            pg = ed.abschnitt_seite()
            ergebnis = SZ.seitenzahl_loeschen_bereich(pg, art, self.blatt)
            if ergebnis:
                ed.page_settings_changed(pg)
        if ergebnis is None:
            self._hinweis("Das lässt sich nur für die erste Seite oder einen ganzen Abschnitt einstellen.")
        elif not ergebnis:
            self._hinweis("Hier steht keine Seitenzahl.")
        if self.aktiv:
            self._laden()
        return ergebnis

    def _hinweis(self, text: str) -> None:
        w = self.ed.window()
        sb = getattr(w, "statusBar", None)
        if callable(sb):
            sb().showMessage(text, 4000)
