"""Rechteck in Bildpunkten (96 dpi): Ursprung links oben, y wächst nach unten."""
from __future__ import annotations

from dataclasses import dataclass

from lunivo_writer.core.geometry.margins import Margins
from lunivo_writer.core.geometry.point import Point
from lunivo_writer.core.geometry.size import Size


@dataclass(frozen=True)
class Rect:
    x: float = 0.0
    y: float = 0.0
    width: float = 0.0
    height: float = 0.0

    @classmethod
    def from_edges(cls, left: float, top: float, right: float, bottom: float) -> "Rect":
        return cls(left, top, right - left, bottom - top)

    @classmethod
    def from_point_size(cls, point: Point, size: Size) -> "Rect":
        return cls(point.x, point.y, size.width, size.height)

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

    @property
    def top_left(self) -> Point:
        return Point(self.x, self.y)

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    @property
    def center(self) -> Point:
        return Point(self.x + self.width / 2, self.y + self.height / 2)

    def is_empty(self) -> bool:
        return self.width <= 0.0 or self.height <= 0.0

    def contains(self, point: Point) -> bool:
        """Liegt der Punkt im Rechteck? Links und oben gehören dazu, rechts und unten nicht."""
        return self.x <= point.x < self.right and self.y <= point.y < self.bottom

    def intersects(self, other: "Rect") -> bool:
        """Überlappen sich beide Flächen? Rechtecke, die sich nur an der Kante berühren, überlappen nicht."""
        return (not self.is_empty() and not other.is_empty()
                and self.x < other.right and other.x < self.right and self.y < other.bottom and other.y < self.bottom)

    def intersected(self, other: "Rect") -> "Rect | None":
        """Die gemeinsame Fläche, ``None`` ohne Überlappung."""
        if not self.intersects(other):
            return None
        return Rect.from_edges(max(self.x, other.x), max(self.y, other.y), min(self.right, other.right), min(self.bottom, other.bottom))

    def united(self, other: "Rect") -> "Rect":
        """Das kleinste Rechteck, das beide enthält (ein leeres Rechteck zählt nicht mit)."""
        if self.is_empty():
            return other
        if other.is_empty():
            return self
        return Rect.from_edges(min(self.x, other.x), min(self.y, other.y), max(self.right, other.right), max(self.bottom, other.bottom))

    def translated(self, dx: float, dy: float) -> "Rect":
        return Rect(self.x + dx, self.y + dy, self.width, self.height)

    def adjusted(self, left: float, top: float, right: float, bottom: float) -> "Rect":
        """Kanten verschieben (wie Qt): positive Werte rücken die Kante nach rechts bzw. unten."""
        return Rect.from_edges(self.x + left, self.y + top, self.right + right, self.bottom + bottom)

    def shrunk(self, margins: Margins) -> "Rect":
        """Das Rechteck innerhalb der Ränder (die Textfläche einer Seite)."""
        return self.adjusted(margins.left, margins.top, -margins.right, -margins.bottom)

    def grown(self, margins: Margins) -> "Rect":
        return self.adjusted(-margins.left, -margins.top, margins.right, margins.bottom)
