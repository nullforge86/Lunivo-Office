"""Unveränderliche Beschreibung von WordArt- und Texteffekten für die Oberfläche."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EffektDaten:
    """Ein Effekt (oder ein Teil davon wie Schatten, Spiegelung, Leuchten, Verlauf) als Schlüssel-Wert-Paare.
    Werte sind Zahlen, Texte, Wahrheitswerte, verschachtelte ``EffektDaten`` oder Folgen davon."""
    werte: tuple[tuple[str, EffektWert], ...] = ()


EffektWert = str | int | float | bool | None | EffektDaten | tuple["EffektWert", ...]


@dataclass(frozen=True)
class EffektVorgabe:
    """Eine benannte Vorgabe des Effekt-Menüs; ``abschnitt`` gruppiert Vorgaben (leer: keine Gruppe)."""
    name: str
    effekt: EffektDaten
    abschnitt: str = ""
