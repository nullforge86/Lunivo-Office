"""Befehle der Funktion „Überprüfen“ für die Oberfläche: liefert die Framework-Befehle für ein Dokument (Kennung) und einen Melder, dessen
Meldungen an die Statusleiste gehen. Die Oberfläche kennt dadurch weder den Kern noch die Dateien des Frameworks."""
from __future__ import annotations

from collections.abc import Callable

from framework.befehle.ueberpruefen import (AenderungenBefehle, AnzeigeBefehle, KommentareBefehle, MarkupBefehle, NotenBefehle,
                                             SCHUTZ_HINWEIS as _HINWEIS, ist_geschuetzt as _geschuetzt)
from framework.ereignisse import Melder
from framework.schnittstellen.datentypen import Art
from framework.schnittstellen import Einstellungen, VorschauPort

def schutz_hinweis() -> str:
    """Hinweis in der Statusleiste, wenn ein Dokumentschutz einen Befehl verhindert."""
    return str(_HINWEIS)


def ist_geschuetzt(schutz: str | None, *arten: str) -> bool:
    return _geschuetzt(schutz, *arten)


def meldungen_an(empfaenger: Callable[[str, int], None]) -> Melder:
    """Ein Melder für die Befehle: jede Meldung geht als (Text, Dauer in ms) an ``empfaenger``."""
    m = Melder()
    m.abonnieren(Art.MELDUNG, lambda e: empfaenger(e.text, int(e.daten.get("dauer_ms", 4000))))
    return m


def kommentare_befehle(kennung: int, melder: Melder) -> KommentareBefehle:
    return KommentareBefehle(kennung, melder)


def aenderungen_befehle(kennung: int, melder: Melder) -> AenderungenBefehle:
    return AenderungenBefehle(kennung, melder)


def noten_befehle(kennung: int) -> NotenBefehle:
    return NotenBefehle(kennung)


def markup_befehle(kennung: int, einstellungen: Einstellungen, melder: Melder) -> MarkupBefehle:
    return MarkupBefehle(kennung, einstellungen, melder)


def anzeige_befehle(kennung: int | None, vorschau: VorschauPort) -> AnzeigeBefehle:
    return AnzeigeBefehle(kennung, vorschau)
