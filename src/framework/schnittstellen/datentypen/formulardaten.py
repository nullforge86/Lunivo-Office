"""Unveränderliche Beschreibung der Formularfelder (Text, Auswahl, Datum, Kontrollkästchen, Schaltfläche) für die Oberfläche."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Feldbeschreibung:
    """Ein Formularfeld: Art, Name und die Angaben der Art (leere Angaben gelten als nicht gesetzt)."""
    art: str
    name: str = ""
    platzhalter: str = ""
    beschriftung: str = ""
    optionen: tuple[str, ...] = ()
    aufschrift: str = ""
    aktion: str = ""
    leer: bool = False                                     # das Feld zeigt nur seinen Platzhalter


@dataclass(frozen=True)
class FeldTreffer:
    """Das Feld an einer Stelle: Stellen im Rohtext (``von`` bis ``bis``) und seine Beschreibung."""
    von: int
    bis: int
    feld: Feldbeschreibung
