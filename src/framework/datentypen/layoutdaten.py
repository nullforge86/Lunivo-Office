"""Seitenübersicht für die Anzeige: Lage und Größe der Seiten im Dokumentfenster, Seitenzahl."""
from __future__ import annotations

from dataclasses import dataclass

from framework.datentypen.zeichenliste import Zeichenliste


@dataclass(frozen=True)
class Seitenansicht:
    nummer: int                                 # ab 1
    x: float
    y: float
    breite: float
    hoehe: float
    inhalt: Zeichenliste | None = None


@dataclass(frozen=True)
class Seitenuebersicht:
    seiten: tuple[Seitenansicht, ...] = ()

    @property
    def anzahl(self) -> int:
        return len(self.seiten)
