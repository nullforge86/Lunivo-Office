"""Grundformen als Vektorpfade ohne Qt: Dreieck, Raute, Vieleck, Stern, Herz, Parallelogramm, Trapez, Blockpfeile, Kreuz, Wolke und Zylinder.

Das sind die Formen, die Word und LibreOffice als Standardformen anbieten und die in Dokumenten am häufigsten vorkommen. ``grundform_pfad(art, r)`` liefert den Umriss
im Rechteck ``r`` (Bildpunkte) oder ``None`` für eine unbekannte Art; ``adj`` verändert, wo es üblich ist, die Proportionen (Anteile 0…1).
"""
from __future__ import annotations

import math

from .rect import Rect


def _vieleck(punkte, r: Rect) -> tuple:
    p = [(r.x + x * r.width, r.y + y * r.height) for x, y in punkte]
    return (("M", *p[0]),) + tuple(("L", *q) for q in p[1:]) + (("Z",),)


def _stern(zacken: int, r: Rect, innen: float = 0.382) -> tuple:
    mx, my = r.x + r.width / 2, r.y + r.height / 2
    pts = []
    for i in range(zacken * 2):
        w = -math.pi / 2 + i * math.pi / zacken
        f = 0.5 if i % 2 == 0 else 0.5 * innen
        pts.append((mx + math.cos(w) * f * r.width, my + math.sin(w) * f * r.height))
    return (("M", *pts[0]),) + tuple(("L", *q) for q in pts[1:]) + (("Z",),)


def _blockpfeil(r: Rect, schaft: float, kopf: float) -> tuple:
    """Blockpfeil nach rechts: ``schaft`` = Anteil der Höhe, ``kopf`` = Anteil der Breite für die Spitze."""
    y0, y1 = (1 - schaft) / 2, (1 + schaft) / 2
    return _vieleck([(0, y0), (1 - kopf, y0), (1 - kopf, 0), (1, 0.5), (1 - kopf, 1), (1 - kopf, y1), (0, y1)], r)


def _gedreht(ops: tuple, r: Rect, viertel: int) -> tuple:
    """Die Pfadanweisungen um ``viertel`` Vierteldrehungen im Uhrzeigersinn um die Mitte von ``r`` drehen (für Pfeile nach unten, links, oben)."""
    mx, my = r.x + r.width / 2, r.y + r.height / 2

    def d(x, y):
        dx, dy = x - mx, y - my
        for _ in range(viertel % 4):
            dx, dy = -dy, dx
        return mx + dx, my + dy
    aus = []
    for o in ops:
        if o[0] in ("M", "L"):
            aus.append((o[0], *d(o[1], o[2])))
        elif o[0] == "C":
            aus.append(("C", *d(o[1], o[2]), *d(o[3], o[4]), *d(o[5], o[6])))
        else:
            aus.append(o)
    return tuple(aus)


def _herz(r: Rect) -> tuple:
    x, y, b, h = r.x, r.y, r.width, r.height
    return (("M", x + b / 2, y + h),
            ("C", x + b * 0.05, y + h * 0.62, x - b * 0.12, y + h * 0.22, x + b * 0.25, y + h * 0.1),
            ("C", x + b * 0.4, y + h * 0.03, x + b / 2, y + h * 0.18, x + b / 2, y + h * 0.3),
            ("C", x + b / 2, y + h * 0.18, x + b * 0.6, y + h * 0.03, x + b * 0.75, y + h * 0.1),
            ("C", x + b * 1.12, y + h * 0.22, x + b * 0.95, y + h * 0.62, x + b / 2, y + h), ("Z",))


def _wolke(r: Rect) -> tuple:
    """Wolke als Kranz aus Bögen: ``n`` Ausbuchtungen auf einer Ellipse."""
    n = 8
    mx, my, rx, ry = r.x + r.width / 2, r.y + r.height / 2, r.width * 0.42, r.height * 0.40
    pts = [(mx + math.cos(2 * math.pi * k / n) * rx, my + math.sin(2 * math.pi * k / n) * ry) for k in range(n)]
    ops = [("M", *pts[0])]
    for k in range(n):
        a, b = pts[k], pts[(k + 1) % n]
        mx2, my2 = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        nx, ny = mx2 - mx, my2 - my
        l = math.hypot(nx, ny) or 1.0
        s = 0.28 * math.hypot(b[0] - a[0], b[1] - a[1]) * 1.4
        cx, cy = mx2 + nx / l * s * 1.5, my2 + ny / l * s * 1.5
        ops.append(("C", a[0] + (cx - a[0]) * 0.9, a[1] + (cy - a[1]) * 0.9, b[0] + (cx - b[0]) * 0.9, b[1] + (cy - b[1]) * 0.9, b[0], b[1]))
    ops.append(("Z",))
    return tuple(ops)


def _zylinder(r: Rect) -> tuple:
    x, y, b, h = r.x, r.y, r.width, r.height
    e = min(h * 0.2, b * 0.5)
    k = 0.5522847498
    rx, ry = b / 2, e / 2
    mx = x + rx
    return (("M", x, y + ry),
            ("C", x, y + ry - k * ry, mx - k * rx, y, mx, y), ("C", mx + k * rx, y, x + b, y + ry - k * ry, x + b, y + ry),
            ("L", x + b, y + h - ry),
            ("C", x + b, y + h - ry + k * ry, mx + k * rx, y + h, mx, y + h), ("C", mx - k * rx, y + h, x, y + h - ry + k * ry, x, y + h - ry), ("Z",),
            ("M", x, y + ry), ("C", x, y + ry + k * ry, mx - k * rx, y + e, mx, y + e), ("C", mx + k * rx, y + e, x + b, y + ry + k * ry, x + b, y + ry))


_PUNKTE = {
    "dreieck": [(0.5, 0), (1, 1), (0, 1)],
    "rechtwinkliges_dreieck": [(0, 0), (1, 1), (0, 1)],
    "raute": [(0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)],
    "fuenfeck": [(0.5, 0), (1, 0.38), (0.81, 1), (0.19, 1), (0, 0.38)],
    "sechseck": [(0.25, 0), (0.75, 0), (1, 0.5), (0.75, 1), (0.25, 1), (0, 0.5)],
    "siebeneck": [(0.5, 0), (0.9, 0.2), (1, 0.62), (0.72, 1), (0.28, 1), (0, 0.62), (0.1, 0.2)],
    "achteck": [(0.29, 0), (0.71, 0), (1, 0.29), (1, 0.71), (0.71, 1), (0.29, 1), (0, 0.71), (0, 0.29)],
    "parallelogramm": [(0.25, 0), (1, 0), (0.75, 1), (0, 1)],
    "trapez": [(0.2, 0), (0.8, 0), (1, 1), (0, 1)],
    "kreuz": [(0.33, 0), (0.67, 0), (0.67, 0.33), (1, 0.33), (1, 0.67), (0.67, 0.67), (0.67, 1), (0.33, 1), (0.33, 0.67), (0, 0.67), (0, 0.33), (0.33, 0.33)],
    "pfeil_fuenfeck": [(0, 0), (0.7, 0), (1, 0.5), (0.7, 1), (0, 1)],
    "chevron": [(0, 0), (0.7, 0), (1, 0.5), (0.7, 1), (0, 1), (0.3, 0.5)],
}
FORMEN = tuple(_PUNKTE) + ("stern", "stern4", "stern6", "stern8", "herz", "wolke", "zylinder", "blockpfeil_rechts", "blockpfeil_links", "blockpfeil_oben", "blockpfeil_unten")


def grundform_pfad(art: str, r: Rect, adj=None):
    """Der Umriss der Grundform ``art`` in ``r`` als Anweisungsfolge für ``VectorPath``; ``None``, wenn die Art unbekannt ist."""
    if art in _PUNKTE:
        return _vieleck(_PUNKTE[art], r)
    if art in ("stern", "stern5"):
        return _stern(5, r)
    if art in ("stern4", "stern6", "stern8"):
        return _stern(int(art[-1]), r, 0.38 if art != "stern4" else 0.25)
    if art == "herz":
        return _herz(r)
    if art == "wolke":
        return _wolke(r)
    if art == "zylinder":
        return _zylinder(r)
    if art.startswith("blockpfeil_"):
        schaft = float(adj[0]) if adj else 0.5
        kopf = float(adj[1]) if adj and len(adj) > 1 else 0.5 * min(1.0, r.height / max(r.width, 1.0))
        rechts = _blockpfeil(r, schaft, kopf)
        viertel = {"rechts": 0, "unten": 1, "links": 2, "oben": 3}.get(art.split("_", 1)[1])
        if viertel is None:
            return None
        if viertel % 2 == 1:                                    # senkrechte Pfeile: im gedrehten Rechteck bauen, dann zurückdrehen
            quer = Rect(r.x + r.width / 2 - r.height / 2, r.y + r.height / 2 - r.width / 2, r.height, r.width)
            return _gedreht(_blockpfeil(quer, schaft, 0.5 * min(1.0, quer.height / max(quer.width, 1.0)) if not adj else kopf), r, viertel)
        return _gedreht(rechts, r, viertel)
    return None
