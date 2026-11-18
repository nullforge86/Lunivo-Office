"""Zeilenmaße: Zeilenhöhe nach Zeilenabstand, Oberlänge und Unterlänge einer Schrift. Ohne Qt."""
from __future__ import annotations

import math

from .engine import FontSpec, TextLayoutEngine


def zeilenhoehe(natuerlich: float, art: str = "single", wert: float = 100.0) -> float:
    """Zeilenhöhe nach Zeilenabstand: ``single`` (wert ignoriert), ``proportional`` (Prozent), ``fixed`` (Bildpunkte), ``min`` (mindestens Bildpunkte)."""
    if art == "proportional":
        return natuerlich * wert / 100.0
    if art == "fixed":
        return float(wert)
    if art == "min":
        return max(natuerlich, float(wert))
    return natuerlich


def zeilenmasse(engine: TextLayoutEngine, font: FontSpec) -> tuple[float, float]:
    """(Oberlänge, Unterlänge) einer Zeile in dieser Schrift: wie bei Qt auf ganze Bildpunkte aufgerundet (die Zeilenhöhe von ``QTextLine`` ist ganzzahlig)."""
    m = engine.font_metrics(font)
    return float(math.ceil(m.ascent - 1e-6)), float(math.ceil(m.descent - 1e-6))
