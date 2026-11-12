"""Textsatz-Schnittstelle ohne Qt (Phase 6 der Qt-Entkopplung, siehe ``dokumentation/architektur/qt-entkopplung.md``).

``TextLayoutEngine`` ist die Stelle, an der Zeilenumbruch, Glyphenpositionen und Schriftmaße herkommen. Die Umsetzung mit Qt liegt in ``adapter/qt/textlayout.py``;
HarfBuzz/FreeType sind als spätere Umsetzung vorgesehen. Zeilenumbruch und Absatzregeln gehören in diese Schicht, nicht in die Shaping-Bibliothek."""
from lunivo_writer.core.textlayout.engine import FontSpec, FontMetrics, GlyphPosition, LineBox, TextLayoutEngine

__all__ = ["FontMetrics", "FontSpec", "GlyphPosition", "LineBox", "TextLayoutEngine"]
