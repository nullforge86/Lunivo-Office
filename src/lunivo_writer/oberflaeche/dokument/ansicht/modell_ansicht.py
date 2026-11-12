"""Ansicht des Dokuments aus dem Kern: Dokumentenmodell → Qt-freier Seitenumbruch (``core.layout``) → Rendering-Backend, mit Schreibmarke, Auswahl, Maus und Tastatur.

Die Ansicht hält keinen eigenen Inhalt. Sie fragt die Bearbeitungssitzung (``core.editing.Sitzung``) über ``sitzung_holen`` ab und ändert das Dokument nur über sie;
im Dokumentfenster ist das die Sitzung des Modell-Spiegels (``editor.modell_spiegel().sitzung()``), der jede Änderung auch im Textdokument des Editors nachspielt.
Damit bleiben Speichern, Befehle und Rückgängig eine Sache. Wo die Schreibmarke steht und wohin sie geht, rechnet ``core.layout.navigation``; gezeichnet wird mit
``adapter.qt.seitenbild.seite_malen`` (derselbe Weg wie Vorlagenkacheln und Modell-PDF).

Eingebaut über ``DocumentTab.set_layout("kern")``; mit ``LUNIVO_KERN_ANSICHT=1`` öffnet jedes Dokument so."""
from __future__ import annotations

import os

from PySide6.QtCore import QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QGuiApplication, QKeySequence, QPainter, QPalette
from PySide6.QtWidgets import QAbstractScrollArea, QApplication, QScrollArea, QWidget

from lunivo_writer.adapter.qt.rendering import QtRenderBackend
from lunivo_writer.adapter.qt.seitenbild import grundschrift, seite_malen
from lunivo_writer.core.editing import Caret
from lunivo_writer.core.geometry import Point
from lunivo_writer.core.layout import navigation as NAV
from lunivo_writer.core.layout import umbrechen
from lunivo_writer.core.layout.seitenumbruch import BLATT_ABSTAND_PX
from lunivo_writer.core.rendering.backend import rgba
from lunivo_writer.core.rendering.seite import zeichne_auswahl, zeichne_cursor
from lunivo_writer.dienste.textsatz import standard_engine
from lunivo_writer.kern.farben import Farbe
from lunivo_writer.modelle.seite import mm_to_px

KERN_ANSICHT = os.environ.get("LUNIVO_KERN_ANSICHT", "0") == "1"       # "1": Dokumente öffnen in der Ansicht aus dem Kern
AUSWAHL_DECKKRAFT = 90                 # Deckkraft der Auswahlfarbe über dem Text (0–255)
SICHT_RAND = 40                        # so viel Platz bleibt beim Rollen um die Schreibmarke
ZEILENWECHSEL = " "               # Umschalt+Eingabe: neue Zeile im selben Absatz
STANDARD_BLATT_MM = (210.0, 297.0)
# Taste → (Bewegung, Bewegung mit Strg)
BEWEGUNG = {Qt.Key_Left: ("links", "wort_links"), Qt.Key_Right: ("rechts", "wort_rechts"), Qt.Key_Up: ("hoch", "hoch"), Qt.Key_Down: ("runter", "runter"),
            Qt.Key_Home: ("zeilenanfang", "anfang"), Qt.Key_End: ("zeilenende", "ende"), Qt.Key_PageUp: ("seite_hoch", "seite_hoch"), Qt.Key_PageDown: ("seite_runter", "seite_runter")}


class ModellAnsicht(QWidget):
    zoomChanged = Signal(float)
    geaendert = Signal()                   # das Dokument wurde über diese Ansicht geändert
    cursorBewegt = Signal()

    ZOOM_MIN, ZOOM_MAX = 0.1, 5.0

    def __init__(self, sitzung_holen, parent=None, engine=None):
        super().__init__(parent)
        self._sitzung_holen = sitzung_holen
        self._engine = engine or standard_engine()
        self._sitzung = None
        self._erg = None
        self._grund = None
        self._x: float | None = None           # gemerkte Spalte der Schreibmarke bei „hoch“/„runter“
        self._an = True
        self._zieht = False
        self._nur_lesen = False
        self.zoom = 1.0
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.IBeamCursor)
        self.setAttribute(Qt.WA_InputMethodEnabled, True)
        self.setAutoFillBackground(False)
        self._blink = QTimer(self)
        self._blink.timeout.connect(self._blinken)
        zeit = QApplication.cursorFlashTime()
        if zeit > 0:
            self._blink.start(zeit // 2)

    # ---- Zustand: Sitzung und gesetztes Dokument --------------------------------------------------------------------------------
    def sitzung(self):
        """Die Bearbeitungssitzung zum jetzigen Stand; wechselt sie (das Dokument wurde außerhalb geändert), gehen Schreibmarke und Auswahl mit, soweit die Stellen noch bestehen."""
        s = self._sitzung_holen()
        if s is not self._sitzung:
            alt = self._sitzung
            self._sitzung = s
            s.beobachter.append(self._modell_geaendert)
            self._erg = None
            if alt is not None:
                s.cursor, s.anker = alt.cursor, alt.anker
        return s

    def ergebnis(self):
        s = self.sitzung()
        if self._erg is None:
            self._erg = umbrechen(s.dok, self._engine)
            self._grund = grundschrift(s.dok)
            liste = NAV.pfade(self._erg)
            if liste and s.cursor.pfad not in self._erg.absaetze:
                s.setzen(Caret(liste[0], 0))
            if s.anker is not None and s.anker.pfad not in self._erg.absaetze:
                s.anker = None
            self._groesse_setzen()
        return self._erg

    def _modell_geaendert(self, _aenderung, _richtung) -> None:
        self._erg = None
        self.update()

    def setReadOnly(self, an: bool) -> None:
        self._nur_lesen = bool(an)

    def isReadOnly(self) -> bool:
        return self._nur_lesen

    def seitenzahl(self) -> int:
        return len(self.ergebnis().seiten)

    # ---- Geometrie ---------------------------------------------------------------------------------------------------------------
    def set_zoom(self, faktor: float) -> None:
        faktor = max(self.ZOOM_MIN, min(self.ZOOM_MAX, round(faktor, 3)))
        if abs(faktor - self.zoom) < 1e-6:
            return
        self.zoom = faktor
        self._groesse_setzen()
        self.update()
        self.zoomChanged.emit(faktor)

    def _blattmass(self, i: int) -> tuple[float, float]:
        einr = self._erg.seiten[i].einrichtung
        b, h = (einr.width_mm, einr.height_mm) if einr is not None else STANDARD_BLATT_MM
        return mm_to_px(b), mm_to_px(h)

    def _groesse_setzen(self) -> None:
        if self._erg is None or not self._erg.seiten:
            return
        breite = max(self._blattmass(i)[0] for i in range(len(self._erg.seiten)))
        letzte = len(self._erg.seiten) - 1
        hoehe = self._erg.seiten[letzte].oben + self._blattmass(letzte)[1]
        self.setMinimumSize(round(breite * self.zoom), round((hoehe + BLATT_ABSTAND_PX) * self.zoom))
        self.updateGeometry()

    def blatt(self, i: int) -> QRectF:
        """Das Blatt ``i`` in den Koordinaten der Ansicht (waagerecht in der Mitte)."""
        b, h = self._blattmass(i)
        w = b * self.zoom
        return QRectF(max(0.0, (self.width() - w) / 2), self._erg.seiten[i].oben * self.zoom, w, h * self.zoom)

    def _stelle(self, pos) -> Caret | None:
        """Die Stelle im Dokument unter einem Punkt der Ansicht (auf dem nächstgelegenen Blatt)."""
        erg = self.ergebnis()
        if not erg.seiten:
            return None
        i = min(range(len(erg.seiten)), key=lambda k: max(self.blatt(k).top() - pos.y(), 0.0, pos.y() - self.blatt(k).bottom()))
        r = self.blatt(i)
        t = erg.treffer(i, Point((pos.x() - r.left()) / self.zoom, (pos.y() - r.top()) / self.zoom))
        return Caret(t[0], t[1]) if t is not None else None

    def cursor_flaeche(self) -> QRectF | None:
        """Die Schreibmarke in den Koordinaten der Ansicht."""
        c = NAV.cursor_rechteck(self.ergebnis(), self.sitzung().cursor)
        if c is None:
            return None
        blatt = self.blatt(c[0])
        r = c[1]
        return QRectF(blatt.left() + r.x * self.zoom, blatt.top() + r.y * self.zoom, max(1.0, r.width * self.zoom), r.height * self.zoom)

    def _sichtbar_machen(self) -> None:
        r = self.cursor_flaeche()
        w = self.parentWidget()
        while r is not None and w is not None:
            if isinstance(w, QScrollArea):
                w.ensureVisible(round(r.center().x()), round(r.center().y()), SICHT_RAND, SICHT_RAND + round(r.height() / 2))
                return
            if isinstance(w, QAbstractScrollArea):
                return
            w = w.parentWidget()

    # ---- Zeichnen ----------------------------------------------------------------------------------------------------------------
    def paintEvent(self, ev) -> None:
        erg, s = self.ergebnis(), self.sitzung()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        auswahl = s.auswahl()
        flaechen = NAV.auswahl_rechtecke(erg, *auswahl) if auswahl else {}
        marke = NAV.cursor_rechteck(erg, s.cursor)
        hell = self.palette().color(QPalette.Highlight)
        auswahlfarbe = (hell.red(), hell.green(), hell.blue(), AUSWAHL_DECKKRAFT)
        sicht = QRectF(ev.rect())
        for i in range(len(erg.seiten)):
            blatt = self.blatt(i)
            if not blatt.intersects(sicht):
                continue
            p.save()
            p.fillRect(blatt, QColor(Farbe.PAPIER))
            p.setClipRect(blatt)
            p.translate(blatt.topLeft())
            p.scale(self.zoom, self.zoom)
            seite_malen(p, s.dok, erg, i, self._engine, self._grund, lambda b, i=i: zeichne_auswahl(b, flaechen.get(i, []), auswahlfarbe))
            if marke is not None and marke[0] == i and self._an and self.hasFocus() and not self._nur_lesen:
                zeichne_cursor(QtRenderBackend(p), marke[1], rgba(Farbe.SCHWARZ))
            p.restore()
        p.end()

    def _blinken(self) -> None:
        self._an = not self._an
        r = self.cursor_flaeche() if self._erg is not None else None
        if r is not None:
            self.update(r.adjusted(-2, -2, 2, 2).toAlignedRect())

    def focusInEvent(self, ev) -> None:
        super().focusInEvent(ev)
        self._an = True
        self.update()

    def focusOutEvent(self, ev) -> None:
        super().focusOutEvent(ev)
        self.update()

    # ---- Schreibmarke und Auswahl ------------------------------------------------------------------------------------------------
    def _gehen(self, ziel: Caret, auswaehlen: bool) -> None:
        s = self.sitzung()
        if auswaehlen:
            s.auswaehlen(s.anker if s.anker is not None else s.cursor, ziel)
        else:
            s.setzen(ziel)
        self._an = True
        self._sichtbar_machen()
        self.update()
        self.cursorBewegt.emit()

    def bewegen(self, art: str, auswaehlen: bool = False) -> None:
        """Die Schreibmarke bewegen (``core.layout.navigation.BEWEGUNGEN``); mit ``auswaehlen`` bleibt der Anker stehen."""
        s = self.sitzung()
        auswahl = s.auswahl()
        if auswahl and not auswaehlen and art in ("links", "rechts"):            # ohne Umschalt fällt die Auswahl auf ihren Rand zusammen
            self._x = None
            self._gehen(auswahl[0] if art == "links" else auswahl[1], False)
            return
        ziel, self._x = NAV.bewegen(self.ergebnis(), s.cursor, art, self._x)
        self._gehen(ziel, auswaehlen)

    def alles_auswaehlen(self) -> None:
        erg = self.ergebnis()
        anfang, _x = NAV.bewegen(erg, self.sitzung().cursor, "anfang")
        ende, _x = NAV.bewegen(erg, self.sitzung().cursor, "ende")
        self.sitzung().auswaehlen(anfang, ende)
        self.update()

    def mousePressEvent(self, ev) -> None:
        if ev.button() != Qt.LeftButton:
            return super().mousePressEvent(ev)
        ziel = self._stelle(ev.position())
        if ziel is not None:
            self._x = None
            self._zieht = True
            self._gehen(ziel, bool(ev.modifiers() & Qt.ShiftModifier))
        self.setFocus()

    def mouseMoveEvent(self, ev) -> None:
        if self._zieht:
            ziel = self._stelle(ev.position())
            if ziel is not None and ziel != self.sitzung().cursor:
                self._gehen(ziel, True)

    def mouseReleaseEvent(self, ev) -> None:
        self._zieht = False
        super().mouseReleaseEvent(ev)

    def mouseDoubleClickEvent(self, ev) -> None:
        ziel = self._stelle(ev.position())
        if ziel is not None:
            von, bis = NAV.wort_bei(self.ergebnis(), ziel)
            self.sitzung().auswaehlen(von, bis)
            self.update()
            self.cursorBewegt.emit()

    # ---- Bearbeiten: alles über die Sitzung ---------------------------------------------------------------------------------------
    def _aendern(self, fn) -> bool:
        """Eine Änderung über die Sitzung ausführen; was die Sitzung ablehnt (zum Beispiel Löschen über Zellgrenzen), lässt das Dokument unverändert."""
        if self._nur_lesen:
            return False
        try:
            fn(self.sitzung())
        except ValueError:
            return False
        self._erg = None
        self._x = None
        self._an = True
        self.ergebnis()
        self._sichtbar_machen()
        self.update()
        self.geaendert.emit()
        return True

    def einfuegen(self, text: str) -> bool:
        return bool(text) and self._aendern(lambda s: s.einfuegen(text))

    def entfernen(self, rueckwaerts: bool, wort: bool = False) -> bool:
        """Die Auswahl löschen, sonst das Zeichen (oder Wort) vor bzw. hinter der Schreibmarke."""
        s = self.sitzung()
        if s.auswahl():
            return self._aendern(lambda s: s.loeschen())
        art = ("wort_links" if wort else "links") if rueckwaerts else ("wort_rechts" if wort else "rechts")
        ziel, _x = NAV.bewegen(self.ergebnis(), s.cursor, art)
        if ziel == s.cursor:
            return False
        return self._aendern(lambda s: s.loeschen(min(ziel, s.cursor), max(ziel, s.cursor)))

    def kopieren(self) -> None:
        s = self.sitzung()
        auswahl = s.auswahl()
        if auswahl:
            QGuiApplication.clipboard().setText(s.text(*auswahl))

    def ausschneiden(self) -> None:
        if self.sitzung().auswahl() and not self._nur_lesen:
            self.kopieren()
            self._aendern(lambda s: s.loeschen())

    def einsetzen(self) -> None:
        self.einfuegen(QGuiApplication.clipboard().text().replace("\r\n", "\n").replace("\r", "\n"))

    def rueckgaengig(self) -> None:
        self._aendern(lambda s: s.rueckgaengig())

    def wiederholen(self) -> None:
        self._aendern(lambda s: s.wiederholen())

    def keyPressEvent(self, ev) -> None:
        taste, mod = ev.key(), ev.modifiers()
        strg, umschalt = bool(mod & Qt.ControlModifier), bool(mod & Qt.ShiftModifier)
        if taste in BEWEGUNG:
            self.bewegen(BEWEGUNG[taste][1 if strg else 0], umschalt)
        elif ev.matches(QKeySequence.Undo):
            self.rueckgaengig()
        elif ev.matches(QKeySequence.Redo):
            self.wiederholen()
        elif ev.matches(QKeySequence.SelectAll):
            self.alles_auswaehlen()
        elif ev.matches(QKeySequence.Copy):
            self.kopieren()
        elif ev.matches(QKeySequence.Cut):
            self.ausschneiden()
        elif ev.matches(QKeySequence.Paste):
            self.einsetzen()
        elif taste in (Qt.Key_Backspace, Qt.Key_Delete):
            self.entfernen(taste == Qt.Key_Backspace, strg)
        elif taste in (Qt.Key_Return, Qt.Key_Enter):
            self.einfuegen(ZEILENWECHSEL if umschalt else "\n")
        elif taste == Qt.Key_Tab:
            self.einfuegen("\t")
        elif ev.text() and ev.text().isprintable() and not (strg and not mod & Qt.AltModifier):       # Strg+Alt (AltGr) liefert Zeichen, Strg allein Befehle
            self.einfuegen(ev.text())
        else:
            return super().keyPressEvent(ev)
        ev.accept()

    def inputMethodEvent(self, ev) -> None:
        if ev.commitString():
            self.einfuegen(ev.commitString())
        ev.accept()

    def inputMethodQuery(self, frage):
        if frage == Qt.ImCursorRectangle:
            r = self.cursor_flaeche()
            return r.toAlignedRect() if r is not None else None
        return super().inputMethodQuery(frage)

    def focusNextPrevChild(self, _weiter: bool) -> bool:
        return False                                                           # die Tabulatortaste gehört dem Text
