"""Silbenfarben (Lesehilfe): unveränderliche Datentypen, die das Framework der Oberfläche übergibt."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SilbenEinstellung:
    """Alle Einstellungen der Lesehilfe „Silben farbig“."""
    an: bool
    palette: str
    eigene: tuple[str, ...]
    anzahl_eigene: int
    darstellung: str
    fett: bool
    einsilbig: bool
    neu_pro_wort: bool
    mindestens: int
    nur_absatz: bool
    drucken: bool
    sprache: str


@dataclass(frozen=True)
class SilbenKatalog:
    """Was das Einstellungsfenster zur Auswahl zeigt, dazu die Standardwerte."""
    paletten: tuple[str, ...]
    darstellungen: tuple[str, ...]
    beispiel: str
    wortmuster: str
    standard: SilbenEinstellung
