"""Netzdiagramm: aus ``core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner`` herausgelöst."""
from __future__ import annotations
import math
from core.geometrie import Point, Rect
from core.layout.drucklayout.ausgabe.backend import Style
from core.diagramme.achsen.skala import _skala
from core.diagramme.typen.kartesisch import _marke
from core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner_hilfen import _Z, _reihenfarbe


# ---- Netz (Radar) -------------------------------------------------------------------------------------------------------------
def _netz(z: _Z, f: Rect) -> None:
    v, b = z.v, z.b
    kat, reihen = v["kat"], v["reihen"]
    namen = list(reihen)
    n = len(kat)
    alle = [w for nm in namen for w in reihen[nm]]
    lo, hi, schritt = _skala(v["wert"], alle, False)
    radius = min(f.width, f.height) / 2 - 24
    mx, my = f.x + f.width / 2, f.y + f.height / 2
    z.teil("zeichnungsbereich", Rect(mx - radius, my - radius, 2 * radius, 2 * radius))
    ringe = max(1, int(round((hi - lo) / schritt)))
    for g in range(1, ringe + 1):
        rr = radius * g / ringe
        ops = [("M", mx + rr * math.cos(-math.pi / 2), my + rr * math.sin(-math.pi / 2))] + [("L", mx + rr * math.cos(-math.pi / 2 + 2 * math.pi * k / n), my + rr * math.sin(-math.pi / 2 + 2 * math.pi * k / n)) for k in range(1, n)] + [("Z",)]
        b.draw_path(ops, Style(color=z.raster, width=1), True, True)
    for k in range(n):
        w = -math.pi / 2 + 2 * math.pi * k / n
        b.draw_line(Point(mx, my), Point(mx + radius * math.cos(w), my + radius * math.sin(w)), Style(color=z.raster, width=1))
        z.text_(str(kat[k]), Rect(mx + (radius + 14) * math.cos(w) - 30, my + (radius + 10) * math.sin(w) - 7, 60, 14), "center")
    for i, nm in enumerate(namen):
        farbe = _reihenfarbe(v, i, v["nummern"][i] if i < len(v["nummern"]) else i)
        pts = [(mx + radius * (reihen[nm][k] - lo) / (hi - lo) * math.cos(-math.pi / 2 + 2 * math.pi * k / n),
                my + radius * (reihen[nm][k] - lo) / (hi - lo) * math.sin(-math.pi / 2 + 2 * math.pi * k / n)) for k in range(n) if k < len(reihen[nm])]
        if len(pts) < 2:
            continue
        ops = [("M", *pts[0])] + [("L", *q) for q in pts[1:]] + [("Z",)]
        if v["art"] == "netz_gefuellt":
            b.draw_path(ops, Style(color=(farbe[0], farbe[1], farbe[2], 120), width=2, filled=True, outline=farbe), True, True)
        else:
            b.draw_path(ops, Style(color=farbe, width=2.5, join="round"), True, True)
        if v["art"] == "netz_punkte":
            for x, y in pts:
                _marke(z, x, y, farbe)
