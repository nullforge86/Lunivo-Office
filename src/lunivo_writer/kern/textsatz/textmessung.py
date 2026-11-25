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
    """(Oberlänge, Unterlänge) einer Zeile in dieser Schrift in Bildpunkten, auf 1/64 Bildpunkt genau: Word und die Referenzdarstellung runden die Zeilenhöhe nicht
    auf ganze Bildpunkte auf; mit Aufrunden wäre jede Zeile bis zu einen Bildpunkt höher und der Text rutscht Absatz für Absatz nach unten."""
    m = engine.font_metrics(font)
    return round(m.ascent * 64) / 64.0, round(m.descent * 64) / 64.0
