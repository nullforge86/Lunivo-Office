"""Textsatz ohne Qt: Schriftmaße aus FreeType, Glyphen und Vorschübe aus HarfBuzz, Zeilenumbruch nach Wortgrenzen.

Die Maße sind Bildpunkte bei 96 dpi wie im übrigen Kern. Die Schriftgröße gilt in ganzen Bildpunkten (wie bei der Qt-Umsetzung, damit die Seitenumbrüche gleich bleiben); gemessen wird ungehintet mit Bruchteilen (Vorschub = Einheiten * Größe / Einheiten je Em).
HarfBuzz formt den ganzen Absatz einmal; die Zeilen werden aus den Vorschüben der Zeichen gebildet (Ligaturen und Zeichenhaufen teilen ihren Vorschub gleichmäßig auf die Zeichen auf)."""
from __future__ import annotations

import freetype
import uharfbuzz as hb

from .engine import FontMetrics, FontSpec, GlyphPosition, LineBox, TextLayoutEngine
from .glyphen import glyphen_positionen, vorschuebe
from .fontdb import SchriftDatenbank, standard_datenbank
from .schrift import PX_JE_PT, Schrift as _Schrift
from .wortumbruch import LEERZEICHEN, UMBRUCH_NACH, umbruch_stellen  # noqa: F401  (hier bisher zu Hause)
from .zeilenumbruch import zeilen_umbrechen


class HarfBuzzEngine(TextLayoutEngine):
    def __init__(self, datenbank: SchriftDatenbank | None = None):
        self._db = datenbank or standard_datenbank
        self._cache: dict[FontSpec, _Schrift] = {}
        self._faces: dict[tuple[str, int], hb.Face] = {}

    # ---- Schrift ----
    def _schrift(self, font: FontSpec) -> _Schrift:
        s = self._cache.get(font)
        if s is not None:
            return s
        schnitt = self._db.finden(font.family, font.weight, font.italic)
        face = self._faces.get((schnitt.pfad, schnitt.index))
        if face is None:
            with open(schnitt.pfad, "rb") as f:
                face = hb.Face(hb.Blob(f.read()), schnitt.index)
            self._faces[(schnitt.pfad, schnitt.index)] = face
        px = float(max(1, round(font.size_pt * PX_JE_PT)))               # ganze Bildpunkte wie die Qt-Umsetzung und die bisherigen Seitenumbrüche
        ft = freetype.Face(schnitt.pfad, schnitt.index)
        upem = ft.units_per_EM or 1000
        k = px / upem
        asc, desc = ft.ascender * k, -ft.descender * k             # Zeilenabstand = Ober- + Unterlänge, der Zusatz ``lineGap`` der Schrift bleibt weg (wie bei Qt)
        hbf = hb.Font(face)
        hbf.scale = (upem, upem)
        s = _Schrift(hbf, upem, asc, desc, asc + desc, px)
        self._cache[font] = s
        return s

    def font_metrics(self, font: FontSpec) -> FontMetrics:
        s = self._schrift(font)
        return FontMetrics(s.ascent, s.descent, s.line_spacing)

    # ---- Formen ----
    def _vorschuebe(self, text: str, s: _Schrift) -> list[float]:
        return vorschuebe(text, s)

    def measure_text(self, text: str, font: FontSpec) -> float:
        return sum(self._vorschuebe(text, self._schrift(font)))

    def shape_text(self, text: str, font: FontSpec) -> list[GlyphPosition]:
        return glyphen_positionen(self._vorschuebe(text, self._schrift(font)))

    # ---- Absatz ----
    def layout_paragraph(self, text: str, font: FontSpec, width: float) -> list[LineBox]:
        s = self._schrift(font)
        adv = self._vorschuebe(text, s)
        return zeilen_umbrechen(text, adv, max(1.0, width), s.line_spacing, s.ascent)


