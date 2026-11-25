"""Eingabe der Dokument-Ansicht: Tastatur, Maus, Eingabemethoden und Zwischenablage. Jede Änderung geht über die Bearbeitungssitzung;
die Ansicht verändert das Dokumentmodell nie selbst.

Die Mischklasse ``EingabeTeil`` setzt voraus, dass die Ansicht ``sitzung``, ``ergebnis()``, ``stelle(punkt)``, ``blatt(i)``, ``cursor_flaeche()``,
``nach_aenderung()`` und ``nach_bewegung()`` bereitstellt (siehe ``dokument_ansicht.py``).
"""
from __future__ import annotations

import base64
import json
import time

from PySide6.QtCore import QMimeData, Qt
from PySide6.QtGui import QGuiApplication, QKeySequence
from PySide6.QtWidgets import QApplication

from core.dokument import Position
from core.geometrie import Rect
from core.dokument.dokument import Auswahl, InlineObjekt, absaetze_in
from core.dokument.serialisierung import bloecke_aus_daten, bloecke_zu_daten
from core.bearbeitung import BearbeitungsFehler
from core.suche.textsuche.suche import position_zu_offset
from core.layout.drucklayout import schreibmarke as SM

MIME_AUSSCHNITT = "application/x-lunivo-ausschnitt"
ZEILENWECHSEL = " "                       # Umschalt+Eingabe: neue Zeile im selben Absatz
# Taste → (Bewegung, Bewegung mit Strg)
BEWEGUNG = {Qt.Key_Left: ("links", "wort_links"), Qt.Key_Right: ("rechts", "wort_rechts"), Qt.Key_Up: ("hoch", "hoch"), Qt.Key_Down: ("runter", "runter"),
            Qt.Key_Home: ("zeilenanfang", "anfang"), Qt.Key_End: ("zeilenende", "ende"), Qt.Key_PageUp: ("seite_hoch", "seite_hoch"),
            Qt.Key_PageDown: ("seite_runter", "seite_runter")}


PFEILE = {Qt.Key_Left: (-1, 0), Qt.Key_Right: (1, 0), Qt.Key_Up: (0, -1), Qt.Key_Down: (0, 1)}


class EingabeTeil:
    # ---- Bearbeiten ------------------------------------------------------------------------------------------------------------
    def aendern(self, fn) -> bool:
        """Anschluss für das Framework (``AenderungsPort``): ``fn(sitzung)`` als eine Änderung ausführen."""
        return self._aendern(fn)

    def lesen(self, abfrage):
        """Anschluss für das Framework (``AenderungsPort``): ``abfrage(sitzung)``, ohne das Dokument zu ändern."""
        return abfrage(self.sitzung)

    def _aendern(self, fn) -> bool:
        """Eine Änderung über die Sitzung ausführen; was die Sitzung ablehnt, lässt das Dokument unverändert."""
        if self.nur_lesen:
            return False
        try:
            if self.vor_aenderung is not None:
                self.vor_aenderung(self.sitzung)
            fn(self.sitzung)
        except BearbeitungsFehler:
            return False
        self._x = None
        self.nach_aenderung()
        return True

    def einfuegen(self, text: str) -> bool:
        return bool(text) and self._aendern(lambda s: s.text_einfuegen(text))

    def entfernen(self, rueckwaerts: bool, wort: bool = False) -> bool:
        """Die Auswahl löschen, sonst das Zeichen (oder Wort) vor bzw. hinter der Schreibmarke."""
        s = self.sitzung
        if not s.auswahl.leer:
            return self._aendern(lambda s: s.loeschen())
        if wort:
            art = "wort_links" if rueckwaerts else "wort_rechts"
            ziel, _x = SM.bewegen(self.ergebnis(), s.auswahl.kopf, art)
            if ziel == s.auswahl.kopf:
                return False
            return self._aendern(lambda s: s.loeschen(Auswahl(s.auswahl.kopf, ziel)))
        return self._aendern(lambda s: s.zeichen_loeschen(vorwaerts=not rueckwaerts))

    def rueckgaengig(self) -> None:
        if not self.nur_lesen and self.sitzung.rueckgaengig():
            self._x = None
            self.nach_aenderung()

    def wiederholen(self) -> None:
        if not self.nur_lesen and self.sitzung.wiederholen():
            self._x = None
            self.nach_aenderung()

    def zeichenformat_umschalten(self, name: str) -> None:
        """Ein Ja/Nein-Zeichenmerkmal (fett, kursiv, unterstrichen …) an der Auswahl umschalten; bei gemischter Auswahl gilt das Format am Anfang."""
        s = self.sitzung
        start, _ende = s._bereich()
        an = bool(s.zeichenformat_bei(start).get(name)) if s.auswahl.leer else bool(s.zeichenformat_bei(Position(start.absatz_id, min(start.versatz + 1, s._absatz(start.absatz_id).laenge))).get(name))
        self._aendern(lambda s: s.zeichenformat_anwenden({name: not an}))

    # ---- Zwischenablage ----------------------------------------------------------------------------------------------------------
    def kopieren(self) -> None:
        s = self.sitzung
        if s.auswahl.leer:
            return
        daten = QMimeData()
        daten.setText(s.text(s.auswahl))
        bloecke = s.ausschnitt(s.auswahl)
        ressourcen = {x.ressource: base64.b64encode(s.dokument.ressourcen[x.ressource]).decode("ascii")
                      for a in absaetze_in(bloecke) for x in a.inhalte
                      if isinstance(x, InlineObjekt) and x.ressource in s.dokument.ressourcen}
        daten.setData(MIME_AUSSCHNITT, json.dumps({"bloecke": bloecke_zu_daten(bloecke), "ressourcen": ressourcen}).encode("utf-8"))
        QGuiApplication.clipboard().setMimeData(daten)

    def ausschneiden(self) -> None:
        if not self.sitzung.auswahl.leer and not self.nur_lesen:
            self.kopieren()
            self._aendern(lambda s: s.loeschen())

    def einsetzen(self) -> None:
        if self.nur_lesen:
            return
        daten = QGuiApplication.clipboard().mimeData()
        if daten is not None and daten.hasFormat(MIME_AUSSCHNITT):
            try:
                inhalt = json.loads(bytes(daten.data(MIME_AUSSCHNITT)).decode("utf-8"))
                bloecke = bloecke_aus_daten(inhalt["bloecke"])
                ressourcen = {k: base64.b64decode(v) for k, v in inhalt.get("ressourcen", {}).items()}
            except (ValueError, KeyError, TypeError):
                bloecke, ressourcen = [], {}
            if bloecke:
                def ein(s):
                    with s.gruppe("Einfügen"):
                        for name, roh in ressourcen.items():
                            if s.dokument.ressourcen.get(name) != roh:
                                s.ressource_setzen(name, roh)
                        s.ausschnitt_einfuegen(bloecke)
                self._aendern(ein)
                return
        if daten is not None:
            self.einfuegen(daten.text().replace("\r\n", "\n").replace("\r", "\n"))

    def alles_auswaehlen(self) -> None:
        d = self.sitzung.dokument
        self.sitzung.setze_auswahl(d.anfang(), d.ende())
        self.nach_bewegung()

    # ---- Schreibmarke und Auswahl ----------------------------------------------------------------------------------------------
    def _gehen(self, ziel: Position, auswaehlen: bool) -> None:
        s = self.sitzung
        s.setze_auswahl(s.auswahl.anker if auswaehlen else ziel, ziel)
        self.nach_bewegung()

    def bewegen(self, art: str, auswaehlen: bool = False) -> None:
        """Die Schreibmarke bewegen (``schreibmarke.BEWEGUNGEN``); mit ``auswaehlen`` bleibt der Anker stehen."""
        s = self.sitzung
        if not s.auswahl.leer and not auswaehlen and art in ("links", "rechts"):         # ohne Umschalt fällt die Auswahl auf ihren Rand zusammen
            start, ende = s._bereich()
            self._x = None
            self._gehen(start if art == "links" else ende, False)
            return
        ziel, self._x = SM.bewegen(self.ergebnis(), s.auswahl.kopf, art, self._x)
        self._gehen(ziel, auswaehlen)

    def tabelle_weiter(self, rueckwaerts: bool) -> bool:
        """Tabulator in einer Tabelle: zur nächsten (vorigen) Zelle; hinter der letzten entsteht eine neue Zeile. ``False`` außerhalb von Tabellen."""
        s = self.sitzung
        stelle = s.tabelle_von(s.auswahl.kopf.absatz_id)
        if stelle is None:
            return False
        t, z, sp = stelle
        zellen = [(zz, ss) for zz in range(t.zeilen) for ss in range(t.spalten) if t.zellen[zz][ss].verdeckt_von is None]
        i = zellen.index(t.anker(z, sp)) + (-1 if rueckwaerts else 1)
        if i < 0:
            return True
        if i >= len(zellen):
            if self.nur_lesen:
                return True
            self._aendern(lambda s: s.zeilen_einfuegen(t.id, t.zeilen))
            zellen = [(zz, ss) for zz in range(t.zeilen) for ss in range(t.spalten) if t.zellen[zz][ss].verdeckt_von is None]
            i = min(i, len(zellen) - 1)
        ziel = s.zelle_anfang(t.id, *zellen[i])
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
        if taste == Qt.Key_Escape and self.tabellen_modus:
            self.tabellen_modus_setzen(None)
            return
        strg, umschalt = bool(mod & Qt.ControlModifier), bool(mod & Qt.ShiftModifier)
        if self.gewaehltes_objekt is not None and taste in PFEILE and not self.nur_lesen and self.objekt_geaendert is not None:
            schritt = 10.0 if umschalt else 1.0
            seite, r = self.sitzung_objekt_rechteck(self.gewaehltes_objekt)
            dx, dy = PFEILE[taste]
            self.objekt_geaendert(self.gewaehltes_objekt, seite, Rect(r.x + dx * schritt, r.y + dy * schritt, r.width, r.height))
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
                self._aendern(lambda s: s.objekt_entfernen(self.gewaehltes_objekt))
                self.gewaehltes_objekt = None
            else:
                self.entfernen(taste == Qt.Key_Backspace, strg)
        elif taste in (Qt.Key_Return, Qt.Key_Enter):
            self.einfuegen(ZEILENWECHSEL if umschalt else "\n")
        elif taste in (Qt.Key_Tab, Qt.Key_Backtab):
            if not self.tabelle_weiter(taste == Qt.Key_Backtab or umschalt):
                self.einfuegen("\t")
        elif taste == Qt.Key_Escape and self.gewaehltes_objekt is not None:
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
            self.gewaehltes_objekt = None
            self.freiAuswahlGeaendert.emit()
            self.update()
        ziel = self.stelle(ev.position())
        if ziel is not None and self._klick_ziel(ziel, ev):
            return
        if ziel is not None:
            self._x = None
            if time.monotonic() - self._doppelklick < QApplication.doubleClickInterval() / 1000.0:      # Dreifachklick: der ganze Absatz
                a = self.sitzung._absatz(ziel.absatz_id)
                self.sitzung.setze_auswahl(Position(a.id, 0), Position(a.id, a.laenge))
                self._doppelklick = 0.0
                self.nach_bewegung()
                return
            self._zieht = True
            self._gehen(ziel, bool(ev.modifiers() & Qt.ShiftModifier))

    def _klick_ziel(self, ziel: Position, ev) -> bool:
        """Klick auf das Zeichen einer Note (öffnet sie), auf ein Formularfeld oder Strg+Klick auf eine Verknüpfung (folgt ihr); ``True``, wenn der Klick
        damit erledigt ist."""
        if self.formular_hook is not None and not self.nur_lesen_formular and self.formular_hook(position_zu_offset(self.sitzung.dokument, ziel)):
            return True
        a = self.sitzung._absatz(ziel.absatz_id)
        for versatz in (ziel.versatz, ziel.versatz - 1):
            if not 0 <= versatz < a.laenge:
                continue
            fmt = self.sitzung.zeichenformat_bei(Position(a.id, versatz + 1))
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
        from core.suche.textsuche.suche import position_zu_offset
        d = self.sitzung.dokument
        objekt = self.objekt_bei(ev.pos())
        if objekt is not None:
            if objekt != self.gewaehltes_objekt:
                self.gewaehltes_objekt = objekt
                self.freiAuswahlGeaendert.emit()
                self.update()
        else:
            ziel = self.stelle(ev.pos())
            if ziel is not None:
                von, bis = self.sitzung._bereich()
                if not (position_zu_offset(d, von) <= position_zu_offset(d, ziel) <= position_zu_offset(d, bis)) or self.sitzung.auswahl.leer:
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
            if ziel is not None and ziel != self.sitzung.auswahl.kopf:
                self._gehen(ziel, True)

    def mouseReleaseEvent(self, ev) -> None:
        if self.freiform_hook is not None and self.freiform_hook("release", ev):
            return
        if self.tabellen_maus_loslassen(ev) or self.objekt_maus_loslassen(ev):
            return
        wurde_gezogen, self._zieht = self._zieht, False
        if wurde_gezogen and not self.sitzung.auswahl.leer and ev.button() == Qt.LeftButton:
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
            von, bis = SM.wort_bei(self.ergebnis(), ziel)
            self.sitzung.setze_auswahl(von, bis)
            self._doppelklick = time.monotonic()
            self.nach_bewegung()

    def wheelEvent(self, ev) -> None:
        if ev.modifiers() & Qt.ControlModifier:                                # Strg + Rad: Zoom
            self.set_zoom(self.zoom * (1.1 if ev.angleDelta().y() > 0 else 1 / 1.1))
            ev.accept()
        else:
            super().wheelEvent(ev)
