"""Textsatz ohne Qt: Schriftmaße aus FreeType, Glyphen und Vorschübe aus HarfBuzz, Zeilenumbruch nach Wortgrenzen.

Die Maße sind Bildpunkte bei 96 dpi wie im übrigen Kern. Die Schriftgröße gilt in ganzen Bildpunkten (wie bei der Qt-Umsetzung, damit die Seitenumbrüche gleich bleiben); gemessen wird ungehintet mit Bruchteilen (Vorschub = Einheiten * Größe / Einheiten je Em).
HarfBuzz formt den ganzen Absatz einmal; die Zeilen werden aus den Vorschüben der Zeichen gebildet (Ligaturen und Zeichenhaufen teilen ihren Vorschub gleichmäßig auf die Zeichen auf)."""
from __future__ import annotations

from dataclasses import dataclass

import freetype
import uharfbuzz as hb

from lunivo_writer.core.textlayout.engine import FontMetrics, FontSpec, GlyphPosition, LineBox, TextLayoutEngine
from lunivo_writer.core.textlayout.fontdb import SchriftDatenbank, standard_datenbank

PX_JE_PT = 96.0 / 72.0
# Zeichen, nach denen eine Zeile enden darf (zusätzlich zum Leerzeichen): Bindestrich, Gedankenstrich, Schrägstrich, weicher Trennstrich, Nullbreitenleerzeichen
UMBRUCH_NACH = "-‐–—/­​"
LEERZEICHEN = " \t          　"        # geschütztes Leerzeichen (U+00A0) bricht nie


@dataclass
class _Schrift:
    hb_font: hb.Font
    upem: int
    ascent: float
    descent: float
    line_spacing: float
    px: float


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
        """Vorschub je Zeichen (Bildpunkte)."""
        if not text:
            return []
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(s.hb_font, buf, {"kern": True, "liga": True})
        k = s.px / s.upem
        je_zeichen = [0.0] * len(text)
        # Cluster = Stelle des ersten Zeichens; mehrere Glyphen eines Clusters und mehrere Zeichen eines Clusters verteilen sich auf die Zeichen
        cluster: dict[int, float] = {}
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            cluster[info.cluster] = cluster.get(info.cluster, 0.0) + pos.x_advance * k
        stellen = sorted(cluster)
        for i, c in enumerate(stellen):
            ende = stellen[i + 1] if i + 1 < len(stellen) else len(text)
            n = max(1, ende - c)
            for j in range(c, min(ende, len(text))):
                je_zeichen[j] = cluster[c] / n
        return je_zeichen

    def measure_text(self, text: str, font: FontSpec) -> float:
        return sum(self._vorschuebe(text, self._schrift(font)))

    def shape_text(self, text: str, font: FontSpec) -> list[GlyphPosition]:
        adv = self._vorschuebe(text, self._schrift(font))
        x, res = 0.0, []
        for i, a in enumerate(adv):
            res.append(GlyphPosition(i, x, a))
            x += a
        return res

    # ---- Absatz ----
    def layout_paragraph(self, text: str, font: FontSpec, width: float) -> list[LineBox]:
        s = self._schrift(font)
        adv = self._vorschuebe(text, s)
        return zeilen_umbrechen(text, adv, max(1.0, width), s.line_spacing, s.ascent)


def umbruch_stellen(text: str) -> list[int]:
    """Stellen, an denen eine Zeile enden darf: der Index des ersten Zeichens der nächsten Zeile (nach Leerzeichen, Bindestrich usw.; Zeilenumbruch erzwingt)."""
    res = []
    for i, c in enumerate(text):
        if c == "\n" or c == " ":
            res.append(i + 1)
        elif i + 1 < len(text) and (c in LEERZEICHEN or c in UMBRUCH_NACH) and text[i + 1] not in LEERZEICHEN:
            res.append(i + 1)
    return res


def zeilen_umbrechen(text: str, vorschuebe: list[float], breite: float, hoehe: float, steig: float) -> list[LineBox]:
    """Zeilen aus den Vorschüben: Wortumbruch, ein zu langes Wort bricht an der Zeichengrenze. Leerzeichen am Zeilenende zählen nicht zur Breite."""
    if not text:
        return [LineBox(0, 0, 0.0, hoehe, steig)]
    zeilen: list[LineBox] = []
    erlaubt = set(umbruch_stellen(text))
    n = len(text)
    start = 0
    while start < n:
        x, ende, letzte = 0.0, start, None
        i = start
        zwang = False
        while i < n:
            c = text[i]
            if c == "\n" or c == " ":
                ende, zwang = i + 1, True
                break
            w = vorschuebe[i]
            sichtbar = x + w if c not in LEERZEICHEN else x                      # Leerzeichen am Zeilenende dürfen überstehen
            if sichtbar > breite + 0.01 and i > start:
                break
            x += w
            i += 1
            if i in erlaubt:
                letzte = i
        else:
            ende = n
        if not zwang and i < n:
            ende = letzte if letzte is not None and letzte > start else max(i, start + 1)
        elif not zwang:
            ende = n
        sicht_ende = ende - 1 if zwang else ende
        while sicht_ende > start and text[sicht_ende - 1] in LEERZEICHEN:
            sicht_ende -= 1
        w = sum(vorschuebe[start:sicht_ende])
        zeilen.append(LineBox(start, ende - start, w, hoehe, steig))
        start = ende
    if text[-1] in "\n ":
        zeilen.append(LineBox(n, 0, 0.0, hoehe, steig))
    return zeilen
