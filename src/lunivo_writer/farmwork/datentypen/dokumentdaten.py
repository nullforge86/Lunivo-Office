"""Auswahl für die Anzeige: Auswahlbereiche als Rechtecke in Seitenkoordinaten (die Oberfläche zeichnet sie)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Rechteck:
    seite: int
    x: float
    y: float
    breite: float
    hoehe: float


@dataclass(frozen=True)
class Auswahlansicht:
    rechtecke: tuple[Rechteck, ...] = ()
    leer: bool = True
