"""Arten der Ereignisse, die das Framework an die Oberfläche meldet (Rückweg)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Art(str, Enum):
    GEAENDERT = "geaendert"         # Dokument oder Zustand hat sich geändert, die Anzeige muss neu gezeichnet werden
    MELDUNG = "meldung"             # Hinweis, Warnung oder Fehler für den Benutzer
    RUECKFRAGE = "rueckfrage"       # das Framework braucht eine Entscheidung; die Antwort kommt als neuer Befehl zurück
    FORTSCHRITT = "fortschritt"     # Fortschritt einer längeren Arbeit
    OEFFNEN = "oeffnen"             # die Oberfläche soll ein Fenster oder einen Dialog öffnen (Text: was, Daten: Parameter)


@dataclass(frozen=True)
class Ereignis:
    art: Art
    text: str = ""
    daten: dict = field(default_factory=dict)
