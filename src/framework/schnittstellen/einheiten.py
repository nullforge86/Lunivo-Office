"""Maßeinheiten für die Oberfläche: Millimeter und Bildpunkte (96 dpi) – dieselbe Umrechnung wie im Kern, als Werte."""
from __future__ import annotations

from core.geometrie import PX_PER_MM as _PX_PER_MM, mm_to_px as _mm_to_px, px_to_mm as _px_to_mm


def px_je_mm() -> float:
    """Bildpunkte je Millimeter (96 dpi)."""
    return float(_PX_PER_MM)


def mm_zu_px(mm: float) -> float:
    return float(_mm_to_px(mm))


def px_zu_mm(px: float) -> float:
    return float(_px_to_mm(px))
