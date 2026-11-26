"""Punkt und Rechteck der Oberfläche in Bildpunkten (96 dpi, Ursprung links oben, y wächst nach unten): eigene Werte, keine Objekte des Kerns."""
from __future__ import annotations

from typing import NamedTuple


class Punkt(NamedTuple):
    x: float = 0.0
    y: float = 0.0

    def translated(self, dx: float, dy: float) -> "Punkt":
        return Punkt(self.x + dx, self.y + dy)


class Rechteck(NamedTuple):
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

    @property
    def left(self) -> float:
        return self.x

    @property
    def top(self) -> float:
        return self.y

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def contains(self, punkt) -> bool:
        """Liegt der Punkt im Rechteck? Links und oben gehören dazu, rechts und unten nicht."""
        return self.x <= punkt.x < self.right and self.y <= punkt.y < self.bottom

    def translated(self, dx: float, dy: float) -> "Rechteck":
        return Rechteck(self.x + dx, self.y + dy, self.width, self.height)

    def adjusted(self, left: float, top: float, right: float, bottom: float) -> "Rechteck":
        """Kanten verschieben (wie Qt): positive Werte rücken die Kante nach rechts bzw. unten."""
        links, oben = self.x + left, self.y + top
        return Rechteck(links, oben, self.right + right - links, self.bottom + bottom - oben)


class Groesse(NamedTuple):
    width: float = 0.0
    height: float = 0.0


class Raender(NamedTuple):
    left: float = 0.0
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0


class Vektorpfad(NamedTuple):
    """Ein Umriss als Pfadanweisungen ohne Qt: ``("M", x, y)``, ``("L", x, y)``, ``("C", x1, y1, x2, y2, x, y)``, ``("Q", …)``, ``("Z",)``,
    ``("E", mx, my, rx, ry)`` (Ellipse) und ``("R", x, y, b, h)`` (Rechteck)."""
    ops: tuple = ()
