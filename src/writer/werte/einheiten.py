"""Maßeinheiten für die Oberfläche: Millimeter und Bildpunkte (96 dpi), über das Framework."""
from __future__ import annotations

from framework.schnittstellen import mm_zu_px as _mm_zu_px, px_je_mm as _px_je_mm, px_zu_mm as _px_zu_mm


def px_je_mm() -> float:
    """Bildpunkte je Millimeter (96 dpi)."""
    return _px_je_mm()


def mm_zu_px(mm: float) -> float:
    return _mm_zu_px(mm)


def px_zu_mm(px: float) -> float:
    return _px_zu_mm(px)
