"""Eigene, unveränderliche Datentypen der Funktion „Überprüfen“ für die Oberfläche."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarkupFilter:
    """Was das Markup zeigt: Kommentare, Einfügungen und Löschungen, ausgewählte Bearbeiter (``None`` = alle), ein Tag (``None`` = alle)."""
    kommentare: bool = True
    einfuegungen: bool = True
    bearbeiter: frozenset[str] | None = None
    zeit: str | None = None


@dataclass(frozen=True)
class EntscheidenZustand:
    """Welche Einträge der Klappen „Annehmen“ und „Ablehnen“ gerade gehen."""
    eine: bool = False
    angezeigte: bool = False
    alle: bool = False
