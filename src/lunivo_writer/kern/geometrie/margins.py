"""Ränder (links, oben, rechts, unten) in Bildpunkten (96 dpi)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Margins:
    left: float = 0.0
    top: float = 0.0
    right: float = 0.0
    bottom: float = 0.0

    @property
    def horizontal(self) -> float:
        return self.left + self.right

    @property
    def vertical(self) -> float:
        return self.top + self.bottom
