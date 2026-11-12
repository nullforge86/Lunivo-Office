"""Die Schnittstelle des Textsatzes. Maße in Bildpunkten (96 dpi), y wächst nach unten."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FontSpec:
    """Eine Schrift: Familie, Größe in Punkt, Gewicht (Qt-Skala: 400 normal, 700 fett) und Kursiv."""
    family: str
    size_pt: float
    weight: int = 400
    italic: bool = False


@dataclass(frozen=True)
class FontMetrics:
    ascent: float
    descent: float
    line_spacing: float


@dataclass(frozen=True)
class GlyphPosition:
    """Stelle eines Zeichens in einer Zeile: ``index`` ist die Zeichenstelle im Text, ``x`` der Abstand vom Zeilenanfang, ``advance`` die Breite."""
    index: int
    x: float
    advance: float


@dataclass(frozen=True)
class LineBox:
    """Eine umgebrochene Zeile: Zeichenbereich im Absatz, Breite, Höhe und Ausrichtung ihrer Glyphen."""
    start: int
    length: int
    width: float
    height: float
    ascent: float


class TextLayoutEngine:
    """Schnittstelle. Umsetzungen überschreiben alle Methoden; die Basisklasse meldet das fehlende Stück, statt zu raten."""

    def font_metrics(self, font: FontSpec) -> FontMetrics:
        raise NotImplementedError

    def measure_text(self, text: str, font: FontSpec) -> float:
        """Breite eines Textes in einer Zeile (ohne Umbruch)."""
        raise NotImplementedError

    def shape_text(self, text: str, font: FontSpec) -> list[GlyphPosition]:
        """Glyphen-Positionen eines Textes in einer Zeile (ohne Umbruch)."""
        raise NotImplementedError

    def layout_paragraph(self, text: str, font: FontSpec, width: float) -> list[LineBox]:
        """Zeilen eines Absatzes bei der Breite ``width``, mit Wortumbruch (lange Wörter an der Zeichengrenze)."""
        raise NotImplementedError
