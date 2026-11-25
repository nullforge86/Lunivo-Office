"""Glyphenkonturen als Pfade: Text wird zu Pfadanweisungen (``M``, ``L``, ``Q``, ``C``, ``Z``), die jede Zeichenfläche füllen kann (gedrehter Text, PDF, Texteffekte).

FreeType liefert die Kontur jeder Glyphe ungehintet in Schrifteinheiten, die Stellen kommen aus ``formen``. Die Größe ist die Bruchgröße der Schrift (``Schrift.px``); es wird
nirgends auf ganze Bildpunkte gerundet."""
from __future__ import annotations

import freetype

from core.formatierung.schrift.formen import forme
from core.formatierung.schrift.schrift import Schrift

_LADEN = freetype.FT_LOAD_NO_SCALE | freetype.FT_LOAD_NO_HINTING | freetype.FT_LOAD_NO_BITMAP
_gemerkt: dict[tuple, list] = {}


def _kontur(s: Schrift, glyphe: int) -> list:
    """Anweisungen der Glyphe in Schrifteinheiten (y nach oben): ``("M", x, y)``, ``("L", x, y)``, ``("Q", cx, cy, x, y)``, ``("C", …)``, ``("Z",)``."""
    schluessel = (s.schluessel, glyphe)
    ops = _gemerkt.get(schluessel)
    if ops is not None:
        return ops
    ops = []
    try:
        s.ft_face.load_glyph(glyphe, _LADEN)
        umriss = s.ft_face.glyph.outline
        if umriss.n_points:
            offen = [False]

            def anfang(a, _):
                if offen[0]:
                    ops.append(("Z",))
                ops.append(("M", a.x, a.y))
                offen[0] = True

            def linie(a, _):
                ops.append(("L", a.x, a.y))

            def kegel(c, a, _):
                ops.append(("Q", c.x, c.y, a.x, a.y))

            def kubisch(c1, c2, a, _):
                ops.append(("C", c1.x, c1.y, c2.x, c2.y, a.x, a.y))

            umriss.decompose(None, move_to=anfang, line_to=linie, conic_to=kegel, cubic_to=kubisch)
            if offen[0]:
                ops.append(("Z",))
    except Exception:                                               # eine nicht lesbare Glyphe bleibt leer
        ops = []
    _gemerkt[schluessel] = ops
    return ops


def text_pfad(s: Schrift, text: str, x: float, grundlinie: float) -> list:
    """Pfadanweisungen des Textes ab ``x`` auf der Grundlinie ``grundlinie`` (Bildpunkte, y nach unten)."""
    if not text:
        return []
    k = s.px / s.upem
    stelle = 0
    pfad: list = []
    for g in forme(s, text):
        gx, gy = x + (stelle + g.dx) * k, grundlinie - g.dy * k
        for op in _kontur(s, g.nummer):
            if op[0] == "Z":
                pfad.append(op)
            else:
                pfad.append((op[0],) + tuple(v for i, w in enumerate(op[1:]) for v in ((gx + w * k) if i % 2 == 0 else (gy - w * k),)))
        stelle += g.vorschub
    return pfad
