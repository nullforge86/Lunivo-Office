"""Kursdiagramm: aus ``core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner`` herausgelöst."""
from __future__ import annotations
from core.geometrie import Point, Rect
from core.layout.drucklayout.ausgabe.backend import Style
from core.diagramme.achsen.skala import _skala, _zahl
from core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner_hilfen import _Z


# ---- Kurs ---------------------------------------------------------------------------------------------------------------------
def _kurs(z: _Z, f: Rect) -> None:
    v, b = z.v, z.b
    kat, reihen = v["kat"], v["reihen"]
    art = v["art"]

    def holen(name: str) -> list:
        return reihen.get(name) or [0.0] * len(kat)
    hoch, tief, schluss = holen("Höchst"), holen("Tiefst"), holen("Schluss")
    eroeff = holen("Eröffnung") if art in ("kurs_ohts", "kurs_vohts") else None
    volumen = holen("Volumen") if art in ("kurs_vhts", "kurs_vohts") else None
    n = len(kat)
    lo, hi, schritt = _skala({}, hoch + tief + schluss, False)
    lo = min(lo, min(tief + schluss) if tief else lo)
    unten_h = 24.0
    vol_h = f.height * 0.22 if volumen else 0.0
    p = Rect(f.x + 40, f.y + 8, f.width - 54, f.height - unten_h - vol_h - 12)
    z.teil("zeichnungsbereich", p)
    ringe = max(1, min(100, int(round((hi - lo) / schritt))))
    for g in range(ringe + 1):
        y = p.bottom - p.height * g / ringe
        b.draw_line(Point(p.x, y), Point(p.right, y), Style(color=z.raster, width=1))
        z.text_(_zahl(lo + g * (hi - lo) / ringe), Rect(f.x + 2, y - 7, 34, 14), "right")
    gruppe = p.width / max(1, n)
    for j in range(n):
        x = p.x + (j + 0.5) * gruppe
        y_h, y_t = p.bottom - (hoch[j] - lo) / (hi - lo) * p.height, p.bottom - (tief[j] - lo) / (hi - lo) * p.height
        y_s = p.bottom - (schluss[j] - lo) / (hi - lo) * p.height
        b.draw_line(Point(x, y_h), Point(x, y_t), Style(color=z.text, width=1.5))
        if eroeff is not None:
            y_e = p.bottom - (eroeff[j] - lo) / (hi - lo) * p.height
            steigt = schluss[j] >= eroeff[j]
            b.draw_rect(Rect(x - gruppe * 0.22, min(y_e, y_s), gruppe * 0.44, max(1.0, abs(y_s - y_e))), Style(color=(255, 255, 255, 255) if steigt else z.text, width=1, filled=True, outline=z.text))
        else:
            b.draw_line(Point(x, y_s), Point(x + gruppe * 0.2, y_s), Style(color=z.text, width=1.5))
        z.text_(str(kat[j]), Rect(x - gruppe / 2, p.bottom + 4, gruppe, 14), "center", "top")
    if volumen:
        top = p.bottom + unten_h
        vmax = max(volumen) or 1.0
        for j in range(n):
            hh = vol_h * volumen[j] / vmax
            b.draw_rect(Rect(p.x + (j + 0.5) * gruppe - gruppe * 0.3, top + vol_h - hh, gruppe * 0.6, hh), Style(color=v["palette"][0], width=0, filled=True))
    b.draw_line(Point(p.x, p.bottom), Point(p.right, p.bottom), Style(color=z.achse, width=1))
