"""Die Textsatz-Engine des Kerns: Schriftauflösung (Datenbank), Formen (HarfBuzz), Maße und Konturen (FreeType), Zeilenumbruch nach Wortgrenzen.

Alles, was über eine Schrift bekannt sein muss — Zeilenhöhe, Breite eines Textes, Stellen der Zeichen, Umbruch eines Absatzes, Glyphenpfade, Deckungsbilder —,
kommt aus dieser einen Klasse. Die Oberfläche reicht nur Schriftnamen und Größen herein und zeigt fertige Bilder."""
from __future__ import annotations

from core.textsatz.engine import FontMetrics, FontSpec, GlyphPosition, LineBox, TextLayoutEngine
from core.textsatz.zeilenumbruch import zeilen_umbrechen

from core.formatierung.schrift import formen, konturen, raster
from core.formatierung.schrift.datenbank import SchriftDatenbank, Schnitt, standard_datenbank
from core.formatierung.schrift.schrift import Schrift, laden


def _stellen(vorschuebe: list[float]) -> list[GlyphPosition]:
    """Stelle, Abstand vom Zeilenanfang und Breite jedes Zeichens."""
    x, stellen = 0.0, []
    for i, breite in enumerate(vorschuebe):
        stellen.append(GlyphPosition(i, x, breite))
        x += breite
    return stellen


class HarfBuzzEngine(TextLayoutEngine):
    def __init__(self, datenbank: SchriftDatenbank | None = None):
        self._datenbank = datenbank or standard_datenbank
        self._geladen: dict[FontSpec, Schrift] = {}
        self._flaechen: dict[tuple[str, int], object] = {}

    # ---- Schrift ----
    def schrift_von(self, font: FontSpec) -> Schrift:
        """Die geladene Schrift (HarfBuzz-Font, FreeType-Schrift, Bruchgröße) für Ausgabewege des Kerns."""
        s = self._geladen.get(font)
        if s is None:
            s = self._geladen[font] = laden(self._datenbank.finden(font.family, font.weight, font.italic), font.size_pt, self._flaechen)
        return s

    def schnitt_von(self, font: FontSpec) -> Schnitt:
        """Der Schnitt (Datei und Index) der Schrift, zum Einbetten."""
        return self._datenbank.finden(font.family, font.weight, font.italic)

    def font_metrics(self, font: FontSpec) -> FontMetrics:
        s = self.schrift_von(font)
        return FontMetrics(s.ascent, s.descent, s.line_spacing)

    # ---- Maße ----
    def measure_text(self, text: str, font: FontSpec) -> float:
        return sum(formen.vorschuebe(self.schrift_von(font), text))

    def shape_text(self, text: str, font: FontSpec) -> list[GlyphPosition]:
        return _stellen(formen.vorschuebe(self.schrift_von(font), text))

    def layout_paragraph(self, text: str, font: FontSpec, width: float) -> list[LineBox]:
        s = self.schrift_von(font)
        return zeilen_umbrechen(text, formen.vorschuebe(s, text), max(1.0, width), s.line_spacing, s.ascent)

    # ---- Ausgabe ----
    def glyphen_pfad(self, text: str, font: FontSpec, x: float, grundlinie: float) -> list:
        """Der Text als Pfadanweisungen (M, L, Q, C, Z) mit der Grundlinie bei ``grundlinie`` in Bruchteilen von Bildpunkten."""
        return konturen.text_pfad(self.schrift_von(font), text, x, grundlinie)

    def text_deckung(self, text: str, font: FontSpec, x: float, grundlinie: float, massstab: float) -> list:
        """Der Text als Deckungsbilder in Geräte-Pixeln (FreeType-Raster in Gerätegröße) für Rasterflächen."""
        return raster.text_deckung(self.schrift_von(font), text, x, grundlinie, massstab)
