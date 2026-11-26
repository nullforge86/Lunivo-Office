"""Steuerung der offenen Dokumente des Hauptfensters: ordnet die Bedienaktionen den Sitzungsbefehlen des Frameworks zu."""
from __future__ import annotations

from collections.abc import Callable, Mapping

from framework.befehle import AUSWAHL, GEAENDERT
from framework.ereignisse import melder
from framework.schnittstellen.datentypen import Art, Ereignis, Geoeffnet
from framework.sitzungen import ANZEIGE, sitzung


def neu(grundschrift: tuple[str, float] | None = None) -> int:
    return sitzung.neu(grundschrift)


def oeffnen_datei(pfad: str, kennwort: str | None = None) -> Geoeffnet:
    """Öffnet die Datei als neues Dokument. Meldet ``KennwortNoetig`` bzw. ``Dateifehler`` (``writer.werte``), wenn das nicht geht."""
    from framework.schnittstellen import Dateifehler as _Dateifehler, KennwortNoetig as _KennwortNoetig
    from writer.werte import Dateifehler, KennwortNoetig
    try:
        return sitzung.oeffnen_datei(pfad, kennwort)
    except _KennwortNoetig as e:
        raise KennwortNoetig(e.falsch) from None
    except _Dateifehler as e:
        raise Dateifehler(str(e)) from None


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


def markup_setzen(kennung: int, an: bool) -> None:
    """Markup (Kommentare und Änderungen) zeigen oder ausblenden; die Ansicht folgt auf ``bei_anzeige``."""
    sitzung.markup_setzen(kennung, an)


def markup_an(kennung: int) -> bool:
    return sitzung.markup_an(kennung)


def markup_filter(kennung: int) -> Mapping[str, bool | str | frozenset[str] | None]:
    return sitzung.markup_filter(kennung)


def bei_anzeige(empfaenger: Callable[[int], None]) -> Callable[[], None]:
    """Meldet ``empfaenger(kennung)`` an, sobald sich die Anzeige eines Dokuments geändert hat (Markup, Verfolgen); gibt die Abmeldung zurück."""
    def weiter(e: Ereignis) -> None:
        if e.text == ANZEIGE:
            empfaenger(int(e.daten.get("kennung", 0)))
    return melder.abonnieren(Art.GEAENDERT, weiter)


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
