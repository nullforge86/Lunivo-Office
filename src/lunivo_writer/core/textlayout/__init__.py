"""Textsatz-Schnittstelle ohne Qt (Phase 6 der Qt-Entkopplung, siehe ``dokumentation/architektur/qt-entkopplung.md``).

``TextLayoutEngine`` ist die Stelle, an der Zeilenumbruch, Glyphenpositionen und Schriftmaße herkommen. Die Umsetzung ist ``HarfBuzzEngine`` im Paket ``core.schrift`` (Schriftdatenbank, HarfBuzz zum Formen, FreeType für Maße, Konturen und Raster). Zeilenumbruch und Absatzregeln gehören in diese Schicht, nicht in die Shaping-Bibliothek."""
from .engine import FontSpec, FontMetrics, GlyphPosition, LineBox, TextLayoutEngine

__all__ = ["FontMetrics", "FontSpec", "GlyphPosition", "LineBox", "TextLayoutEngine"]
