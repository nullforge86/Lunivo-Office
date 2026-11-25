"""Text formen: HarfBuzz setzt Zeichen zu Glyphen (Kerning, Ligaturen, Verschiebungen). Das Ergebnis gilt in Schrifteinheiten und ist unabhängig von der Größe; Vorschübe,
Konturen und Raster der Glyphen bauen alle darauf auf, so stimmen Layout und Darstellung immer überein."""
from __future__ import annotations

from typing import NamedTuple

import uharfbuzz as hb

from core.formatierung.schrift.schrift import Schrift

_MERKEN = 8192
_gemerkt: dict[tuple, tuple] = {}


class Glyphe(NamedTuple):
    nummer: int           # Glyphennummer in der Schrift
    cluster: int          # Stelle des ersten Zeichens im Text
    vorschub: int         # Schrifteinheiten
    dx: int
    dy: int


def forme(s: Schrift, text: str) -> tuple[Glyphe, ...]:
    """Die Glyphen des Textes in einer Zeile."""
    schluessel = (s.schluessel, text)
    glyphen = _gemerkt.get(schluessel)
    if glyphen is None:
        puffer = hb.Buffer()
        puffer.add_str(text)
        puffer.guess_segment_properties()
        hb.shape(s.hb_font, puffer, {"kern": True, "liga": True})
        glyphen = tuple(Glyphe(i.codepoint, i.cluster, p.x_advance, p.x_offset, p.y_offset) for i, p in zip(puffer.glyph_infos, puffer.glyph_positions))
        if len(_gemerkt) >= _MERKEN:
            _gemerkt.clear()
        _gemerkt[schluessel] = glyphen
    return glyphen


def vorschuebe(s: Schrift, text: str) -> list[float]:
    """Vorschub je Zeichen in Bildpunkten. Mehrere Glyphen eines Clusters und mehrere Zeichen eines Clusters (Ligaturen, Zeichenhaufen) teilen ihren Vorschub gleichmäßig auf."""
    if not text:
        return []
    k = s.px / s.upem
    je_cluster: dict[int, float] = {}
    for g in forme(s, text):
        je_cluster[g.cluster] = je_cluster.get(g.cluster, 0.0) + g.vorschub * k
    je_zeichen = [0.0] * len(text)
    stellen = sorted(je_cluster)
    for i, anfang in enumerate(stellen):
        ende = stellen[i + 1] if i + 1 < len(stellen) else len(text)
        anzahl = max(1, ende - anfang)
        for j in range(anfang, min(ende, len(text))):
            je_zeichen[j] = je_cluster[anfang] / anzahl
    return je_zeichen
