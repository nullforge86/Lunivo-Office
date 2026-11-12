"""Größe in Bildpunkten (96 dpi)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Size:
    width: float = 0.0
    height: float = 0.0

    def is_empty(self) -> bool:
        return self.width <= 0.0 or self.height <= 0.0

    def scaled(self, factor: float) -> "Size":
        return Size(self.width * factor, self.height * factor)
