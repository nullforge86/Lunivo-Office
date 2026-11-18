"""Schriftbeschreibung ↔ ``QFont`` für die Rendering-Adapter: Der Kern beschreibt Schriften als ``FontSpec`` (Punkt), Qt zeichnet mit ``QFont``.

Hier steckt kein Textsatz: Zeilenumbruch, Glyphenpositionen und Schriftmaße kommen ausschließlich aus ``core.textlayout`` (``HarfBuzzEngine``).
Die Maße sind die Bildpunkte bei 96 dpi wie im übrigen Kern (Schriftgröße in Punkt wird mit 96/72 in Bildpunkte umgerechnet)."""
from __future__ import annotations

from PySide6.QtGui import QFont

from lunivo_writer.core.textlayout import FontSpec

PX_JE_PT = 96.0 / 72.0


def _schrift(font: FontSpec) -> QFont:
    f = QFont(font.family)
    f.setPixelSize(max(1, round(font.size_pt * PX_JE_PT)))
    f.setWeight(QFont.Weight.Bold if font.weight >= 600 else QFont.Weight.Normal)
    f.setItalic(font.italic)
    return f


def _fontspec_aus(f: QFont) -> FontSpec:
    """``FontSpec`` zu einem ``QFont`` (Größe in Punkt, wie ``_schrift`` sie wieder in ganze Bildpunkte rechnet)."""
    px = f.pixelSize() if f.pixelSize() > 0 else round(f.pointSizeF() * PX_JE_PT)
    return FontSpec(f.family(), px / PX_JE_PT, 700 if f.weight() >= QFont.Weight.DemiBold else 400, f.italic())
