"""Steuerung der offenen Dokumente des Hauptfensters: ordnet die Bedienaktionen den Sitzungsbefehlen des Frameworks zu."""
from __future__ import annotations

from collections.abc import Callable

from framework.befehle import AUSWAHL, GEAENDERT
from framework.ereignisse import melder
from framework.schnittstellen.datentypen import Art, Ereignis, Geoeffnet
from framework.sitzungen import sitzung


def neu(grundschrift: tuple[str, float] | None = None) -> int:
    return sitzung.neu(grundschrift)


def oeffnen_datei(pfad: str, kennwort: str | None = None) -> Geoeffnet:
    return sitzung.oeffnen_datei(pfad, kennwort)


def schliessen(kennung: int) -> None:
    sitzung.schliessen(kennung)


def aktivieren(kennung: int) -> None:
    sitzung.aktivieren(kennung)


def bearbeiter_setzen(kennung: int, name: str) -> None:
    sitzung.bearbeiter_setzen(kennung, name)


def nur_lesen_setzen(kennung: int, an: bool) -> None:
    sitzung.nur_lesen_setzen(kennung, an)


def layout_option_setzen(kennung: int, name: str, wert: float | bool | None) -> None:
    """Layout-Option der Ansicht (Lesehilfe, Web-Layout), damit Seitenzahlen im Framework wie auf dem Bildschirm zählen."""
    sitzung.layout_option_setzen(kennung, name, None if wert is None else (bool(wert) if isinstance(wert, bool) else float(wert)))


def bei_aenderung(empfaenger: Callable[[int], None]) -> Callable[[], None]:
    """Meldet ``empfaenger(kennung)`` an, sobald das Framework ein Dokument geändert hat; gibt die Abmeldung zurück."""
    def weiter(e: Ereignis) -> None:
        if e.text == GEAENDERT:
            empfaenger(int(e.daten.get("kennung", 0)))
    return melder.abonnieren(Art.GEAENDERT, weiter)


def bei_auswahl(empfaenger: Callable[[int], None]) -> Callable[[], None]:
    """Meldet ``empfaenger(kennung)`` an, sobald das Framework nur die Auswahl gesetzt hat (Sprung); gibt die Abmeldung zurück."""
    def weiter(e: Ereignis) -> None:
        if e.text == AUSWAHL:
            empfaenger(int(e.daten.get("kennung", 0)))
    return melder.abonnieren(Art.GEAENDERT, weiter)
