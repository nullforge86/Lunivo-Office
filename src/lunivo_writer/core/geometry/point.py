"""Punkt in Bildpunkten (96 dpi, wie ``modelle/seite.py``), y wächst nach unten."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float = 0.0
    y: float = 0.0

    def translated(self, dx: float, dy: float) -> "Point":
        return Point(self.x + dx, self.y + dy)
