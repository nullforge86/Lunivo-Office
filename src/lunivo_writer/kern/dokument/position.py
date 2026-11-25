"""Gemeinsame Positionsangaben innerhalb eines Dokuments."""

from __future__ import annotations

from dataclasses import dataclass

Pfad = tuple[int, ...]


@dataclass(frozen=True, order=True)
class Caret:
    pfad: Pfad
    versatz: int = 0
