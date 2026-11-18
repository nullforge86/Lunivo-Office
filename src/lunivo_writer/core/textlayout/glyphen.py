"""Glyphen und Vorschübe: HarfBuzz formt den Text einer Zeile, der Vorschub je Cluster verteilt sich gleichmäßig auf die Zeichen (Ligaturen, Zeichenhaufen). Ohne Qt."""
from __future__ import annotations

import uharfbuzz as hb

from .engine import GlyphPosition
from .schrift import Schrift


def vorschuebe(text: str, s: Schrift) -> list[float]:
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


def glyphen_positionen(vorschuebe_je_zeichen: list[float]) -> list[GlyphPosition]:
    """Stelle, Abstand vom Zeilenanfang und Breite jedes Zeichens."""
    x, res = 0.0, []
    for i, a in enumerate(vorschuebe_je_zeichen):
        res.append(GlyphPosition(i, x, a))
        x += a
    return res
