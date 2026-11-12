"""Neutrale Werte für Formateigenschaften (ohne Qt): was eine Eigenschaft eines Zeichen-, Absatz-, Tabellen- oder Rahmenformats annehmen kann."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
    a: int = 255


@dataclass(frozen=True)
class Brush:
    """Pinsel; ``style`` ist der Musterindex (0 = kein Pinsel, 1 = Vollfarbe, weitere Muster zählen wie in Qt). Farbverläufe und Bildmuster kennt das Modell noch nicht."""
    style: int
    color: Color


@dataclass(frozen=True)
class GradientBrush:
    """Pinsel mit Farbverlauf: ``kind`` ``linear`` (``punkte`` = x1, y1, x2, y2), ``radial`` (Mitte x, y, Radius, Brennpunkt x, y) oder ``conical`` (Mitte x, y, Winkel);
    ``stops`` = ((Stelle 0…1, Farbe), …), ``spread`` und ``mode`` wie bei Qt (0 pad, 1 reflect, 2 repeat; 0 logisch, 1 Gerät, 2 Objekt)."""
    kind: str
    punkte: tuple[float, ...]
    stops: tuple[tuple[float, Color], ...]
    spread: int = 0
    mode: int = 0


@dataclass(frozen=True)
class TextureBrush:
    """Pinsel mit Bildmuster: ``style`` der Musterindex, ``png`` das Muster als PNG."""
    style: int
    png: bytes


@dataclass(frozen=True)
class Pen:
    """Stift (zum Beispiel die Kontur von Text): Pinsel, Breite, Strichart, Linienende und Ecken (Zahlen wie bei Qt)."""
    brush: object
    width: float
    style: int = 1
    cap: int = 0
    join: int = 0


@dataclass(frozen=True)
class Length:
    """Längenangabe: ``kind`` ist ``variable``, ``fixed`` (Bildpunkte) oder ``percentage`` (Prozent)."""
    kind: str
    value: float


@dataclass(frozen=True)
class LineSpacing:
    """Absatzzeilenabstand: ``single``, ``proportional`` (Prozent), ``multiple`` (Faktor), ``fixed`` oder ``minimum`` (Bildpunkte)."""
    kind: str
    value: float


@dataclass(frozen=True)
class RowHeight:
    """Tabellenzeilenhöhe: ``minimum`` oder ``exact`` in Bildpunkten."""
    kind: Literal["minimum", "exact"]
    value_px: float


@dataclass(frozen=True)
class TabStop:
    """Tabstopp: Position in Bildpunkten, Art (Zählung wie in Qt: 0 links, 1 rechts, 2 zentriert, 3 Trennzeichen) und Trennzeichen."""
    position: float
    kind: int
    delimiter: str = ""


# Ein Wert ist ein Grundtyp, einer der Typen oben oder ein Tupel solcher Werte (Listen).
PropertyValue = object
