"""Aktionen der Knöpfe auf dem Blatt (Kopf- und Fußzeile): Seitenzahl einfügen, neu aufbauen, Zahlenart, löschen. Jede Aktion ruft einen Befehl
über ``writer`` auf; danach füllt der Bearbeiter die Felder neu."""
from __future__ import annotations

from writer.funktionen import bearbeiten as _bearbeiten
from writer.funktionen.kopffuss import blatttexte as T
from vcl.qt.widgets.bausteine.abstaende import KOPFFUSS_HINWEIS_MS


class SeitenzahlAktionenTeil:
    """Baustein des ``KopfFussBearbeiter``: was die Leiste auslöst."""

    def _neu_zeigen(self) -> None:
        if self.aktiv:
            self._laden()
            self._platzieren()

    def seitenzahl_einfuegen(self, ausrichtung: str, muster: str, zahlenart: str, bereich: str) -> None:
        """Seitenzahl in die Zeile setzen, die gerade bearbeitet wird; ``bereich``: ganzes Dokument, ab der aktuellen Seite oder der Abschnitt."""
        self.speichern()
        ed = self.ed
        abschnitt, zone = ed.abschnitt_nr(), self.zone
        ed.ansicht._befehl(lambda: _bearbeiten.seitenzahl_setzen(ed.kennung, bereich, None, abschnitt, zone, ausrichtung, muster, zahlenart))
        ed.pageApplied.emit()
        self._neu_zeigen()

    def erste_nummer(self) -> int:
        """Die Nummer, mit der die Seitennummerierung des Abschnitts beginnt."""
        return max(1, int(self.ed.abschnitt_seite().seiten_start or 0))

    def nummerierung_beginnt_neu(self) -> bool:
        return int(self.ed.abschnitt_seite().seiten_start or 0) > 0

    def start_setzen(self, nummer: int) -> None:
        """Startwert der Seitennummerierung; ``0``: die Nummerierung des vorigen Abschnitts fortsetzen."""
        self.aendern(lambda seite: setattr(seite, "seiten_start", max(0, nummer)))

    def seitenzahlenformat(self) -> str:
        return self.ed.abschnitt_seite().seiten_format

    def seitenzahlenformat_setzen(self, zahlenart: str) -> None:
        self.aendern(lambda seite: setattr(seite, "seiten_format", zahlenart))

    def seitenzahl_loeschen(self, art: str) -> bool | None:
        """Seitenzahl entfernen (Schlüssel aus ``blattklappen.LOESCHEN``). ``True``/``False``: geändert / gab keine; ``None``: so nicht darstellbar."""
        self.speichern()
        ed = self.ed
        abschnitt, blatt = ed.abschnitt_nr(), self.blatt
        ergebnis = []

        def befehl() -> bool:
            ergebnis.append(_bearbeiten.kopffuss_seitenzahl_loeschen(ed.kennung, abschnitt, art, blatt))
            return bool(ergebnis[0])
        ed.ansicht._befehl(befehl)
        ed.pageApplied.emit()
        if ergebnis[0] is None:
            self._hinweis(T.HINWEIS_NICHT_DARSTELLBAR)
        elif not ergebnis[0]:
            self._hinweis(T.HINWEIS_KEINE_SEITENZAHL)
        self._neu_zeigen()
        return ergebnis[0]

    def _hinweis(self, text: str) -> None:
        leiste = getattr(self.ed.ansicht.window(), "statusBar", None)
        if callable(leiste):
            leiste().showMessage(text, KOPFFUSS_HINWEIS_MS)
