"""Kopf- und Fußzeile direkt auf der Seite bearbeiten (Einfügen ▸ Kopf- und Fußzeile, Doppelklick in den Seitenrand).

    b = editor.kopffuss()                 # der Bearbeiter des Editors (wird beim ersten Aufruf angelegt)
    b.starte("kopf")                      # oder "fuss"; ``b.aktiv``, ``b.beende()``, ``b.wechseln()``, ``b.abschnitt_springen(+1)``

Gespeichert wird in der Seiteneinrichtung des Abschnitts; die Seite wird nicht anders gezeichnet. Über Kopf- und Fußbereich des Blattes liegen zwei
randlose Textfelder mit gestricheltem Rahmen, dazu Linie und Etikett; am aktiven Bereich hängen die Leiste mit den Seitenzahl-Knöpfen und das
Absatz-Symbol. Esc oder Doppelklick in den Text beenden.

Der Bearbeiter ist aus Bausteinen zusammengesetzt: ``lage.py`` (wo die Teile liegen), ``zeilenformat.py`` (Ausrichtung und Schrift der Zeile),
``seitenzahl_aktionen.py`` (was die Leiste auslöst). Hier stehen Start, Ende, Laden und Speichern. Knöpfe, Klappen und Texte beschreibt
``writer.funktionen.kopffuss``."""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QTimer, Signal
from PySide6.QtWidgets import QToolTip

from writer.funktionen import bearbeiten as _bearbeiten
from writer.funktionen.kopffuss import blatttexte as T
from vcl.qt.widgets.bausteine.abstaende import KOPFFUSS_SPEICHERN_MS
from vcl.qt.widgets.dokumentansicht.kopffuss.absatz_knopf import KopfFussAbsatzKnopf
from vcl.qt.widgets.dokumentansicht.kopffuss.bild_aktionen import BildAktionenTeil
from vcl.qt.widgets.dokumentansicht.kopffuss.etikett import KopfFussEtikett
from vcl.qt.widgets.dokumentansicht.kopffuss.kopffuss_feld import KopfFussFeld
from vcl.qt.widgets.dokumentansicht.kopffuss.kopffuss_leiste import KopfFussLeiste
from vcl.qt.widgets.dokumentansicht.kopffuss.lage import LageTeil
from vcl.qt.widgets.dokumentansicht.kopffuss.linie import KopfFussLinie
from vcl.qt.widgets.dokumentansicht.kopffuss.seitenzahl_aktionen import SeitenzahlAktionenTeil
from vcl.qt.widgets.dokumentansicht.kopffuss.verlauf import VerlaufTeil
from vcl.qt.widgets.dokumentansicht.kopffuss.zeilenformat import ZeilenformatTeil


class KopfFussBearbeiter(LageTeil, ZeilenformatTeil, SeitenzahlAktionenTeil, BildAktionenTeil, VerlaufTeil, QObject):
    gestartet = Signal()
    beendet = Signal()

    def __init__(self, editor):
        super().__init__(editor)
        self.ed = editor
        self.aktiv = False
        self.im_feld = False                                    # die Schreibmarke steht im Kopf-/Fußfeld
        self.zone = T.ZONE_VORGABE
        self.blatt = 0
        self.felder, self.linien, self.etiketten = {}, {}, {}
        self.leiste = self.absatz = None
        self._abbilder = {}                                     # Id eines Bildes der Zeile → sein Abbild über den Feldern
        self._abbild_stand = None                               # wofür die Abbilder zuletzt gelegt wurden (Stand des Dokuments, Zoom, Blatt)
        self._laedt = False
        self._verlauf_beginnen()
        self._zeit = QTimer(self)
        self._zeit.setSingleShot(True)
        self._zeit.setInterval(KOPFFUSS_SPEICHERN_MS)
        self._zeit.timeout.connect(self.speichern)
        editor.viewport().installEventFilter(self)

    @property
    def feld(self) -> KopfFussFeld | None:
        """Das Feld des aktiven Bereichs (``zone``); ``None``, solange noch nie gestartet."""
        return self.felder.get(self.zone)

    def _teile(self) -> list:
        teile = [w for z in T.ZONEN for w in (self.linien.get(z), self.felder.get(z), self.etiketten.get(z))] + [self.leiste, self.absatz]
        return [w for w in teile if w is not None]

    def _teile_bauen(self) -> None:
        flaeche = self.ed.viewport()
        for z in T.ZONEN:
            f = self.felder[z] = KopfFussFeld(flaeche, z)
            f.schliessen.connect(self.beende)
            f.textChanged.connect(self._geaendert)
            f.fokus.connect(self._fokus)
            f.document().undoCommandAdded.connect(lambda z=z: self._text_gemerkt(z))
            self.linien[z] = KopfFussLinie(flaeche)
            self.etiketten[z] = KopfFussEtikett(T.ZONENNAMEN[z], flaeche)
        self.leiste = KopfFussLeiste(flaeche, self)
        self.absatz = KopfFussAbsatzKnopf(flaeche, self)

    # ---- Start und Ende -------------------------------------------------------------------------------------------------------------------
    def starte(self, zone: str = T.ZONE_VORGABE, blatt: int | None = None) -> bool:
        ed = self.ed
        if ed.web:                                              # die Webansicht hat keine Blätter und damit keinen Kopf- und Fußbereich
            return False
        if self.aktiv:
            self.speichern()
        self.zone = zone if zone in T.ZONEN else T.ZONE_VORGABE
        self.blatt = self._cursor_blatt() if blatt is None else blatt
        if not self.felder:
            self._teile_bauen()
        war_aktiv, self.aktiv = self.aktiv, True
        self.im_feld = True
        ed.ansicht.marke_folgen = False                         # beim Speichern rollt die Ansicht nicht zur Schreibmarke im Text zurück
        if not war_aktiv:
            self.absatz.ausgeblendet = False
        self._laden()
        self._platzieren()
        for w in self._teile():
            w.setVisible(not (w is self.absatz and self.absatz.ausgeblendet))
            w.raise_()
        self._ins_bild_holen()
        self.feld.setFocus()
        if not war_aktiv:
            self.gestartet.emit()
        return True

    def beende(self) -> None:
        if not self.aktiv:
            return
        self.speichern()
        self.aktiv = False
        self.im_feld = False
        self.ed.ansicht.marke_folgen = True
        for w in self._teile():
            w.hide()
        self._bilder_verbergen()
        self.ed.viewport().update()
        self.ed.setFocus()
        self.beendet.emit()

    def wechseln(self) -> None:
        """Zwischen Kopf- und Fußzeile springen: die Schreibmarke geht ins andere Feld, Leiste und Absatz-Symbol ziehen mit."""
        if self.aktiv:
            self.starte(next(z for z in T.ZONEN if z != self.zone), self.blatt)

    def abschnitt_springen(self, schritt: int) -> bool:
        """Zur Kopf- bzw. Fußzeile des vorigen/nächsten Abschnitts; ``False``, wenn es keinen gibt."""
        ed = self.ed
        ziel = ed.abschnitt_nr() + schritt
        if ziel < 0 or ziel >= _bearbeiten.dok_abschnitte_anzahl(ed.kennung):
            return False
        absatz = _bearbeiten.dok_abschnitt_erster_absatz(ed.kennung, ziel)
        if absatz is None:
            return False
        self.speichern()
        _bearbeiten.auswahl_setzen(ed.kennung, (absatz, 0), (absatz, 0))
        ed.ansicht.nach_bewegung()
        if self.aktiv:
            self.starte(self.zone)
        return True

    def _fokus(self, zone: str) -> None:
        """Klick oder Schreibmarke im anderen Bereich: er wird der aktive, Leiste und Absatz-Symbol ziehen dorthin."""
        if self.aktiv:
            self.im_feld = True
        if not self.aktiv or self._laedt or zone == self.zone:
            return
        self.zone = zone
        self._leiste_laden(self.ed.abschnitt_seite())
        self._platzieren()

    # ---- Seite und Text -------------------------------------------------------------------------------------------------------------------
    def _cursor_blatt(self) -> int:
        try:
            return max(0, int(self.ed._blatt_bei_y(self.ed.cursorRect().center().y())))
        except (AttributeError, IndexError, ValueError):
            return 0

    def _blatt_zeilen(self) -> tuple[str, str, str, str, str]:
        """(Feldname Kopf, Feldname Fuß, angezeigte Seitenzahl, Ausrichtung Kopf, Ausrichtung Fuß) des bearbeiteten Blattes."""
        return _bearbeiten.kopffuss_blatt(self.ed.kennung, self.ed.abschnitt_nr(), self.blatt)

    def _feldname(self, zone: str | None = None) -> str:
        kopf, fuss, _nummer, _ak, _af = self._blatt_zeilen()
        return dict(zip(T.ZONEN, (kopf, fuss)))[zone or self.zone]

    def hf(self, seite=None, zone: str | None = None):
        """Die Kopf- oder Fußzeile (Text, Ausrichtung, Zeichenformat) des bearbeiteten Blattes aus der Seiteneinrichtung."""
        seite = seite or self.ed.abschnitt_seite()
        return getattr(seite, self._feldname(zone))

    def _laden(self) -> None:
        """Beide Felder (Kopf und Fuß) des bearbeiteten Blattes füllen."""
        self._textschritte_verwerfen()
        seite = self.ed.abschnitt_seite()
        kopf, fuss, nummer, kopf_ausrichtung, fuss_ausrichtung = self._blatt_zeilen()
        zahlen = {T.FELD_SEITE: nummer, T.FELD_SEITEN: str(max(1, int(self.ed.page_count or 1)))}
        for z, feldname, ausrichtung in zip(T.ZONEN, (kopf, fuss), (kopf_ausrichtung, fuss_ausrichtung)):
            zeile = getattr(seite, feldname)
            self._laedt = True
            self.felder[z].felder_setzen(zeile.text, zahlen)
            self._laedt = False
            self._ausrichten(z, ausrichtung)
            self._basis_anwenden(z, zeile)
            self.felder[z].document().clearUndoRedoStacks()
            self.etiketten[z].text_setzen(T.etikett(z, bool(seite.diff_even), feldname))
        self._leiste_laden(seite)

    def _leiste_laden(self, seite) -> None:
        """Die Leiste zeigt die Knöpfe, die zur aktiven Zeile passen: mit oder ohne Seitenzahl."""
        self.leiste.zahl_zeigen(T.MARKE_SEITENZAHL in self.hf(seite).text)

    def _geaendert(self) -> None:
        if not self._laedt and self.aktiv:
            self._zeit.start()

    def speichern(self) -> None:
        """Den Text der Felder in die Seiteneinrichtung des Abschnitts schreiben (sofort; beim Tippen nach kurzer Pause)."""
        self._zeit.stop()
        if not self.aktiv or not self.felder:
            return
        seite = self.ed.abschnitt_seite()
        geaendert = False
        for z in T.ZONEN:
            feldname = self._feldname(z)
            zeile = getattr(seite, feldname)
            text = self.felder[z].text_lesen().strip("\n")
            if text != zeile.text:
                setattr(seite, feldname, zeile.kopie(text))
                geaendert = True
        if geaendert:
            self.ed.page_settings_changed(seite)
            self._leiste_laden(seite)
            self._platzieren()

    def aendern(self, aendere, neu_laden: bool = True) -> None:
        """``aendere(seite)`` auf die Einrichtung des aktuellen Abschnitts anwenden und speichern; danach die Felder neu füllen."""
        self.speichern()
        seite = self.ed.abschnitt_seite()
        if aendere(seite) is False:
            return
        self.ed.page_settings_changed(seite)
        if self.aktiv and neu_laden:
            self._laden()
            self._platzieren()

    def tabstopp_einfuegen(self) -> None:
        if self.aktiv:
            self.feld.insertPlainText(T.TABULATOR)
            self.feld.setFocus()

    # ---- Maus in der Ansicht ----------------------------------------------------------------------------------------------------------------
    def eventFilter(self, o, e) -> bool:
        try:
            if o is not self.ed.viewport():
                return False
            art = e.type()
            if self.aktiv and art in (QEvent.Resize, QEvent.Paint):
                self._platzieren()
            elif self.aktiv and art == QEvent.MouseButtonPress:
                self.im_feld = False                            # Klick ins Dokument: die Werkzeuge wirken wieder auf den Text
            elif art == QEvent.ToolTip and not self.ed.web:
                ziel = self._zone_bei(e.pos())
                if ziel is not None:                            # über dem Kopf- oder Fußbereich: sagen, wie man ihn bearbeitet
                    QToolTip.showText(e.globalPos(), T.HINWEIS_DOPPELKLICK.format(name=T.ZONENNAMEN[ziel[0]]), self.ed.viewport())
                    return True
            elif art == QEvent.MouseButtonDblClick and not self.ed.web:
                ziel = self._zone_bei(e.position())
                if ziel is not None and not self.aktiv:         # Doppelklick in den Seitenrand: dort bearbeiten
                    fenster = self.ed.ansicht.window()
                    if hasattr(fenster, "kopffuss_starten"):
                        fenster.kopffuss_starten(self.ed, ziel[0] == T.ZONE_VORGABE, ziel[1])
                        return True
                elif ziel is None and self.aktiv:               # Doppelklick in den Text: beenden
                    self.beende()
                    return True
        except RuntimeError:                                    # Editor beim Beenden schon abgebaut
            pass
        return False
