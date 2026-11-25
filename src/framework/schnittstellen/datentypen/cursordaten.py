"""Schreibmarke für die Anzeige: Lage und Höhe in Seitenkoordinaten."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Schreibmarke:
    seite: int
    x: float
    y: float
    hoehe: float
    sichtbar: bool = True
