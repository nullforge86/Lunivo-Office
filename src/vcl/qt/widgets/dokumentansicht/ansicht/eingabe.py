"""Eingabe der Dokument-Ansicht: Tastatur, Maus, Eingabemethoden und Zwischenablage. Jede Änderung geht über die Bearbeitungssitzung;
die Ansicht verändert das Dokumentmodell nie selbst.

Die Mischklasse ``EingabeTeil`` setzt voraus, dass die Ansicht ``kennung``, ``ergebnis()``, ``stelle(punkt)``, ``blatt(i)``, ``cursor_flaeche()``,
``nach_aenderung()`` und ``nach_bewegung()`` bereitstellt (siehe ``dokument_ansicht.py``).
"""
from __future__ import annotations

import time

from PySide6.QtCore import QMimeData, QPointF, Qt
from PySide6.QtGui import QGuiApplication, QKeySequence
from PySide6.QtWidgets import QApplication

from writer.funktionen import ansicht as AN
from writer.funktionen import bearbeiten as ST
from writer.werte import Bereich, Rechteck, Stelle
from writer.funktionen import bearbeiten as _bearbeiten

MIME_AUSSCHNITT = "application/x-lunivo-ausschnitt"
ZEILENWECHSEL = " "                       # Umschalt+Eingabe: neue Zeile im selben Absatz
# Taste → (Bewegung, Bewegung mit Strg)
BEWEGUNG = {Qt.Key_Left: ("links", "wort_links"), Qt.Key_Right: ("rechts", "wort_rechts"), Qt.Key_Up: ("hoch", "hoch"), Qt.Key_Down: ("runter", "runter"),
            Qt.Key_Home: ("zeilenanfang", "anfang"), Qt.Key_End: ("zeilenende", "ende"), Qt.Key_PageUp: ("seite_hoch", "seite_hoch"),
            Qt.Key_PageDown: ("seite_runter", "seite_runter")}


PFEILE = {Qt.Key_Left: (-1, 0), Qt.Key_Right: (1, 0), Qt.Key_Up: (0, -1), Qt.Key_Down: (0, 1)}


class EingabeTeil:
    # ---- Bearbeiten ------------------------------------------------------------------------------------------------------------
    def _befehl(self, befehl) -> bool:
        """Einen Befehl des Frameworks als eine Änderung ausführen: ``befehl()`` → ``False``, wenn der Kern ablehnt (das Dokument bleibt unverändert)."""
        if self.nur_lesen:
            return False
        if self.vor_aenderung is not None:
            self.vor_aenderung()
        if not befehl():
            return False
        self._x = None
        self.nach_aenderung()
        return True

    def einfuegen(self, text: str) -> bool:
        return bool(text) and self._befehl(lambda: _bearbeiten.aenderung_text_einfuegen(self.kennung, text))

    def entfernen(self, rueckwaerts: bool, wort: bool = False) -> bool:
        """Die Auswahl löschen, sonst das Zeichen (oder Wort) vor bzw. hinter der Schreibmarke."""
        kopf = ST.auswahl(self.kennung)
        if not kopf.leer:
            return self._befehl(lambda: _bearbeiten.aenderung_loeschen(self.kennung))
        kopf = kopf.kopf
        if wort:
            art = "wort_links" if rueckwaerts else "wort_rechts"
            self.ergebnis()
            ziel, _x = AN.bewegen(self.kennung, kopf, art)
            if ziel == kopf:
                return False
            return self._befehl(lambda: _bearbeiten.aenderung_loeschen_bis(self.kennung, (ziel[0], ziel[1])))
        return self._befehl(lambda: _bearbeiten.aenderung_zeichen_loeschen(self.kennung, vorwaerts=not rueckwaerts))

    def rueckgaengig(self) -> None:
        if not self.nur_lesen and _bearbeiten.rueckgaengig(self.kennung):
            self._x = None
            self.nach_aenderung()

    def wiederholen(self) -> None:
        if not self.nur_lesen and _bearbeiten.wiederholen(self.kennung):
            self._x = None
            self.nach_aenderung()

    def zeichenformat_umschalten(self, name: str) -> None:
        """Ein Ja/Nein-Zeichenmerkmal (fett, kursiv, unterstrichen …) an der Auswahl umschalten; bei gemischter Auswahl gilt das Format am Anfang."""
        k = self.kennung
        start, _ende = ST.auswahl_bereich(k)
        an = bool(ST.zeichenformat_bei(k, start).get(name)) if ST.auswahl(k).leer else bool(ST.zeichenformat_bei(k, Stelle(start.absatz_id, min(start.versatz + 1, ST.absatz_laenge(k, start.absatz_id)))).get(name))
        self._befehl(lambda: _bearbeiten.aenderung_zeichenformat_anwenden(self.kennung, {name: not an}))

    # ---- Zwischenablage ----------------------------------------------------------------------------------------------------------
    def kopieren(self) -> None:
        ausschnitt = ST.ausschnitt_kopieren(self.kennung)
        if ausschnitt is None:
            return
        daten = QMimeData()
        daten.setText(ausschnitt[0])
        daten.setData(MIME_AUSSCHNITT, ausschnitt[1].encode("utf-8"))
        QGuiApplication.clipboard().setMimeData(daten)

    def ausschneiden(self) -> None:
        if not ST.auswahl(self.kennung).leer and not self.nur_lesen:
            self.kopieren()
            self._befehl(lambda: _bearbeiten.aenderung_loeschen(self.kennung))

    def einsetzen(self) -> None:
        if self.nur_lesen:
            return
        daten = QGuiApplication.clipboard().mimeData()
        if daten is not None and daten.hasFormat(MIME_AUSSCHNITT):
            try:
                inhalt = bytes(daten.data(MIME_AUSSCHNITT)).decode("utf-8")
            except ValueError:
                inhalt = ""
            if inhalt and ST.ausschnitt_gueltig(inhalt):
                self._befehl(lambda: ST.ausschnitt_einsetzen(self.kennung, inhalt))
                return
        if daten is not None:
            self.einfuegen(daten.text().replace("\r\n", "\n").replace("\r", "\n"))

    def alles_auswaehlen(self) -> None:
        ST.alles_auswaehlen(self.kennung)
        self.nach_bewegung()

    # ---- Schreibmarke und Auswahl ----------------------------------------------------------------------------------------------
    def _gehen(self, ziel: Stelle, auswaehlen: bool) -> None:
        ST.gehen(self.kennung, ziel, auswaehlen)
        self.nach_bewegung()

    def bewegen(self, art: str, auswaehlen: bool = False) -> None:
        """Die Schreibmarke bewegen (``schreibmarke.BEWEGUNGEN``); mit ``auswaehlen`` bleibt der Anker stehen."""
        a = ST.auswahl(self.kennung)
        if not a.leer and not auswaehlen and art in ("links", "rechts"):         # ohne Umschalt fällt die Auswahl auf ihren Rand zusammen
            start, ende = ST.auswahl_bereich(self.kennung)
            self._x = None
            self._gehen(start if art == "links" else ende, False)
            return
        self.ergebnis()
        ziel, self._x = AN.bewegen(self.kennung, a.kopf, art, self._x)
        self._gehen(ziel, auswaehlen)

    def tabelle_weiter(self, rueckwaerts: bool) -> bool:
        """Tabulator in einer Tabelle: zur nächsten (vorigen) Zelle; hinter der letzten entsteht eine neue Zeile. ``False`` außerhalb von Tabellen."""
        k = self.kennung
        stelle = ST.tabellenzellen(k, ST.auswahl(k).kopf.absatz_id)
        if stelle is None:
            return False
        tid, zeilen, zellen, anker = stelle
        i = zellen.index(anker) + (-1 if rueckwaerts else 1)
        if i < 0:
            return True
        if i >= len(zellen):
            if self.nur_lesen:
                return True
            self._befehl(lambda: _bearbeiten.aenderung_zeilen_einfuegen(self.kennung, tid, zeilen))
            zellen = ST.sichtbare_zellen(k, tid)
            i = min(i, len(zellen) - 1)
        ziel = ST.zelle_anfang(k, tid, *zellen[i])
        self._gehen(ziel, False)
        return True

    # ---- Tastatur ----------------------------------------------------------------------------------------------------------------
    def keyPressEvent(self, ev) -> None:
        taste, mod = ev.key(), ev.modifiers()
        if self.gliederung_hook is not None and taste in (Qt.Key_Left, Qt.Key_Right) and mod & Qt.AltModifier and mod & Qt.ShiftModifier:
            self.gliederung_hook(-1 if taste == Qt.Key_Left else 1)
            return
        if self.freiform_taste is not None and self.freiform_taste(ev):
            return
        if self.gewaehltes_objekt is not None and self.objekt_teil_taste is not None and not self.nur_lesen and self.objekt_teil_taste(ev):
            return
        if taste == Qt.Key_Escape and self.tabellen_modus:
            self.tabellen_modus_setzen(None)
            return
        strg, umschalt = bool(mod & Qt.ControlModifier), bool(mod & Qt.ShiftModifier)
        if self.gewaehltes_objekt is not None and taste in PFEILE and not self.nur_lesen and self.objekt_geaendert is not None:
            schritt = 10.0 if umschalt else 1.0
            seite, r = self.sitzung_objekt_rechteck(self.gewaehltes_objekt)
            dx, dy = PFEILE[taste]
            self.objekt_geaendert(self.gewaehltes_objekt, seite, Rechteck(r.x + dx * schritt, r.y + dy * schritt, r.width, r.height))
            self.nach_aenderung()
        elif taste in BEWEGUNG:
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
        elif strg and taste in (Qt.Key_B, Qt.Key_I, Qt.Key_U) and not mod & Qt.AltModifier:
            self.zeichenformat_umschalten({Qt.Key_B: "fett", Qt.Key_I: "kursiv", Qt.Key_U: "unterstrichen"}[taste])
        elif taste in (Qt.Key_Backspace, Qt.Key_Delete):
            if self.gewaehltes_objekt is not None and not self.nur_lesen:
                self._befehl(lambda: _bearbeiten.aenderung_objekt_entfernen(self.kennung, self.gewaehltes_objekt))
                self.gewaehltes_objekt = None
            elif not self.tabelle_taste_loeschen(taste == Qt.Key_Backspace):
                self.entfernen(taste == Qt.Key_Backspace, strg)
        elif taste in (Qt.Key_Return, Qt.Key_Enter):
            self.einfuegen(ZEILENWECHSEL if umschalt else "\n")
        elif taste in (Qt.Key_Tab, Qt.Key_Backtab):
            if not self.tabelle_weiter(taste == Qt.Key_Backtab or umschalt):
                self.einfuegen("\t")
        elif taste == Qt.Key_Escape and self.gewaehltes_objekt is not None:
            self.objekt_abwahl_melden()
            self.gewaehltes_objekt = None
            self.update()
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

    # ---- Maus --------------------------------------------------------------------------------------------------------------------
    def mousePressEvent(self, ev) -> None:
        if ev.button() != Qt.LeftButton:
            return super().mousePressEvent(ev)
        self.setFocus()
        if self.freiform_hook is not None and self.freiform_hook("press", ev):
            return
        if self.blasen_maus_druecken(ev) or self.tabellen_maus_druecken(ev) or self.objekt_maus_druecken(ev):
            return
        if self.gewaehltes_objekt is not None:
            self.objekt_abwahl_melden()
            self.gewaehltes_objekt = None
            self.freiAuswahlGeaendert.emit()
            self.update()
        ziel = self.stelle(ev.position())
        if ziel is not None and self._klick_ziel(ziel, ev):
            return
        if ziel is not None:
            self._x = None
            if time.monotonic() - self._doppelklick < QApplication.doubleClickInterval() / 1000.0:      # Dreifachklick: der ganze Absatz
                ST.auswahl_setzen(self.kennung, Stelle(ziel.absatz_id, 0), Stelle(ziel.absatz_id, ST.absatz_laenge(self.kennung, ziel.absatz_id)))
                self._doppelklick = 0.0
                self.nach_bewegung()
                return
            self._zieht = True
            self._gehen(ziel, bool(ev.modifiers() & Qt.ShiftModifier))

    def _klick_ziel(self, ziel: Stelle, ev) -> bool:
        """Klick auf das Zeichen einer Note (öffnet sie), auf ein Formularfeld oder Strg+Klick auf eine Verknüpfung (folgt ihr); ``True``, wenn der Klick
        damit erledigt ist."""
        k = self.kennung
        if self.formular_hook is not None and not self.nur_lesen_formular and self.formular_hook(ST.stelle_im_text(k, ziel)):
            return True
        laenge = ST.absatz_laenge(k, ziel.absatz_id)
        for versatz in (ziel.versatz, ziel.versatz - 1):
            if not 0 <= versatz < laenge:
                continue
            fmt = ST.zeichenformat_bei(k, Stelle(ziel.absatz_id, versatz + 1))
            note = fmt.get("note")
            art, _s, nr = str(note or "").partition(":")
            if nr.isdigit():
                self.noteAngeklickt.emit(art, int(nr))
                return True
            if fmt.get("link") and ev.modifiers() & Qt.ControlModifier:
                self.linkAngeklickt.emit(str(fmt["link"]))
                return True
        return False

    def contextMenuEvent(self, ev) -> None:
        """Rechtsklick: Auswahl an die Stelle setzen (außerhalb der Auswahl) bzw. das Objekt wählen, dann das Menü anfordern."""
        k = self.kennung
        objekt = self.objekt_bei(ev.pos())
        if objekt is not None:
            if objekt != self.gewaehltes_objekt:
                self.objekt_abwahl_melden()
                self.gewaehltes_objekt = objekt
                self.freiAuswahlGeaendert.emit()
                self.update()
            elif self.objekt_teil_klick is not None and not self.nur_lesen:      # Rechtsklick in das gewählte Diagramm/SmartArt wählt den Teil darunter
                self.objekt_teil_klick(QPointF(ev.pos()))
        else:
            ziel = self.stelle(ev.pos())
            if ziel is not None:
                von, bis = ST.auswahl_bereich(k)
                if not (ST.stelle_im_text(k, von) <= ST.stelle_im_text(k, ziel) <= ST.stelle_im_text(k, bis)) or ST.auswahl(k).leer:
                    self.gewaehltes_objekt = None
                    self._gehen(ziel, False)
        self.kontextGewuenscht.emit(ev.globalPos())

    def mouseMoveEvent(self, ev) -> None:
        if self.freiform_hook is not None and self.freiform_hook("move", ev):
            return
        if self.tabellen_maus_bewegen(ev) or self.objekt_maus_bewegen(ev):
            return
        if self._zieht:
            ziel = self.stelle(ev.position())
            if ziel is not None and ziel != ST.auswahl(self.kennung).kopf:
                self._gehen(ziel, True)

    def mouseReleaseEvent(self, ev) -> None:
        if self.freiform_hook is not None and self.freiform_hook("release", ev):
            return
        if self.tabellen_maus_loslassen(ev) or self.objekt_maus_loslassen(ev):
            return
        wurde_gezogen, self._zieht = self._zieht, False
        if wurde_gezogen and not ST.auswahl(self.kennung).leer and ev.button() == Qt.LeftButton:
            self.auswahlBeendet.emit(ev.globalPosition().toPoint())
        super().mouseReleaseEvent(ev)

    def mouseDoubleClickEvent(self, ev) -> None:
        if self.freiform_hook is not None and self.freiform_hook("doppel", ev):
            return
        if self.blasen_doppelklick(ev):
            return
        objekt = self.objekt_bei(ev.position())
        if objekt is not None:
            if self.objekt_doppelklick is not None:
                self.objekt_doppelklick(objekt)
            return
        ziel = self.stelle(ev.position())
        if ziel is not None:
            self.ergebnis()
            von, bis = AN.wort_bei(self.kennung, ziel)
            ST.auswahl_setzen(self.kennung, von, bis)
            self._doppelklick = time.monotonic()
            self.nach_bewegung()

    def wheelEvent(self, ev) -> None:
        if ev.modifiers() & Qt.ControlModifier:                                # Strg + Rad: Zoom
            self.set_zoom(self.zoom * (1.1 if ev.angleDelta().y() > 0 else 1 / 1.1))
            ev.accept()
        else:
            super().wheelEvent(ev)
