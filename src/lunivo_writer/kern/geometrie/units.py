"""Einheiten der Qt-freien Geometrie: Seiteneinstellungen in Millimetern, Layoutkoordinaten in Bildpunkten bei 96 dpi."""
from __future__ import annotations

PX_PER_MM = 96.0 / 25.4


def mm_to_px(mm: float) -> float:
    return mm * PX_PER_MM


def px_to_mm(px: float) -> float:
    return px / PX_PER_MM


def umbruchraster(px: float) -> float:
    """Auf 1/64 Bildpunkt abschneiden, damit Qt-Zeilengrenzen seitenübergreifend stabil bleiben."""
    return int(px * 64) / 64
