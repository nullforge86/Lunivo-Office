"""Zeichenliste: die Zeichenbefehle einer Seite als eigene, unveränderliche Datentypen. Die Oberfläche malt nur diese Liste (mit QPainter).

Das Framework übersetzt die Zeichenbefehle des Kerns (``kern/rendering``) in diese Typen; die Oberfläche setzt keinen Kern-Vertrag um."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Zeichenbefehl:
    art: str                                    # z. B. "rechteck", "linie", "text", "bild", "pfad"
    daten: tuple = ()                           # art-spezifische Werte als unveränderliches Tupel
    farbe: str = ""                             # "#rrggbb" oder "#aarrggbb"; leer = keine Füllung


@dataclass(frozen=True)
class Zeichenliste:
    breite: float
    hoehe: float
    befehle: tuple[Zeichenbefehl, ...] = ()
