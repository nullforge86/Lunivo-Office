"""Der Rahmen um die Seite („Rahmen und Schattierung“ ▸ Seitenrand) ohne Qt: Lage, Abstände, Kunstrahmen und Linienrahmen als Zeichenanweisungen für ein ``RenderBackend``.

Ein Seitenrahmen ist ein Wörterbuch (``PageSettings.border``): ``farbe``, ``breite_pt``, ``art`` (Linienart), ``seiten`` („tblr“), ``abstand`` („oben,unten,links,rechts“ in pt, sonst ``abstand_mm``),
``messen`` („text“ oder „seitenrand“), ``kopf``/``fuss`` (Kopf-/Fußzeile umgeben), ``kunst`` (Art des Rahmens, leer = Linie). ``page`` liefert die Ränder in mm (``margin_*_mm``)."""
from __future__ import annotations

import math

from lunivo_writer.core.geometry import Rect
from lunivo_writer.core.rendering.backend import RenderBackend, Style, rgba
from lunivo_writer.core.rendering.linien import zeichne_rahmen

PX_JE_MM = 96.0 / 25.4
KOPF_MM = 12.5                      # Abstand der Kopf- und Fußzeile vom Blattrand, soweit der Rahmen sie umgeben soll
SCHWARZ = "#000000"


def abstaende_pt(b: dict) -> tuple[float, float, float, float]:
    """(oben, unten, links, rechts) in pt."""
    try:
        o, u, l, r = (float(x) for x in str(b.get("abstand", "")).split(","))
        return o, u, l, r
    except ValueError:
        pt = b.get("abstand_mm", 8.0) / 25.4 * 72
        return pt, pt, pt, pt


def rechteck(b: dict, page, seite: Rect) -> Rect:
    """Das Rechteck des Rahmens in Bildpunkten, auf einer Seite mit dem Rechteck ``seite``."""
    o, u, l, r = (x * 96 / 72 for x in abstaende_pt(b))
    if b.get("messen", "seitenrand") == "text":
        ml, mt, mr, mb = (m * PX_JE_MM for m in (page.margin_left_mm, page.margin_top_mm, page.margin_right_mm, page.margin_bottom_mm))
        text = seite.adjusted(ml, mt, -mr, -mb)
        oben = seite.y + min(mt, KOPF_MM * PX_JE_MM) if b.get("kopf") else text.y
        unten = seite.bottom - min(mb, KOPF_MM * PX_JE_MM) if b.get("fuss") else text.bottom
        return Rect(text.x - l, oben - o, text.width + l + r, unten - oben + o + u)
    return seite.adjusted(l, o, -r, -u)


def _vieleck(punkte: list[tuple[float, float]]) -> list:
    return [("M", *punkte[0])] + [("L", *pt) for pt in punkte[1:]] + [("L", *punkte[0])]


def _figur(art: str, mitte: tuple[float, float], groesse: float) -> list:
    """Umriss einer Figur als Pfadanweisungen (``core.rendering.RenderBackend.draw_path``)."""
    mx, my = mitte
    r = groesse / 2
    if art == "stars":
        pt = [(mx + (r if i % 2 == 0 else r * 0.42) * math.sin(i * math.pi / 5), my - (r if i % 2 == 0 else r * 0.42) * math.cos(i * math.pi / 5))
              for i in range(10)]
        return _vieleck(pt)
    if art == "hearts":
        return [("M", mx, my + r),
                ("C", mx - r * 1.6, my - r * 0.2, mx - r * 0.5, my - r * 1.2, mx, my - r * 0.35),
                ("C", mx + r * 0.5, my - r * 1.2, mx + r * 1.6, my - r * 0.2, mx, my + r)]
    if art == "triangles":
        return _vieleck([(mx, my - r), (mx + r, my + r), (mx - r, my + r)])
    return _vieleck([(mx, my - r), (mx + r * 0.7, my), (mx, my + r), (mx - r * 0.7, my)])      # Edelsteine: Rauten


def kunst_zeichnen(backend: RenderBackend, rect: Rect, art: str, breite_px: float, farbe: tuple[int, int, int, int]) -> None:
    """Einen Kunstrahmen entlang der Kanten: Figuren in regelmäßigem Abstand (Zickzack als Linienzug)."""
    g = max(8.0, breite_px)
    figur_stil = Style(color=farbe, width=1, filled=True)
    zickzack_stil = Style(color=farbe, width=max(1.0, g / 6))
    ol, orr, ur, ul = (rect.x, rect.y), (rect.x + rect.width, rect.y), (rect.x + rect.width, rect.y + rect.height), (rect.x, rect.y + rect.height)
    for a, z in ((ol, orr), (orr, ur), (ur, ul), (ul, ol)):
        laenge = math.hypot(z[0] - a[0], z[1] - a[1])
        n = max(2, int(laenge // (g * 1.5)))
        if art == "zigZag":
            ops = [("M", a[0], a[1])]
            dx, dy = (z[0] - a[0]) / n, (z[1] - a[1]) / n
            nx, ny = -dy / max(1e-6, math.hypot(dx, dy)) * g / 2, dx / max(1e-6, math.hypot(dx, dy)) * g / 2
            for i in range(1, n + 1):
                s = 1 if i % 2 else -1
                ops.append(("L", a[0] + dx * (i - 0.5) + nx * s, a[1] + dy * (i - 0.5) + ny * s))
                ops.append(("L", a[0] + dx * i, a[1] + dy * i))
            backend.draw_path(ops, zickzack_stil)
            continue
        for i in range(n):
            t = (i + 0.5) / n
            backend.draw_path(_figur(art, (a[0] + (z[0] - a[0]) * t, a[1] + (z[1] - a[1]) * t), g), figur_stil)


def zeichnen(backend: RenderBackend, b: dict, page, seite: Rect) -> None:
    """Den Seitenrahmen auf eine Seite zeichnen (Linie in ihrer Art oder Kunstrahmen)."""
    rect = rechteck(b, page, seite)
    breite = float(b.get("breite_pt", 1.0))
    if b.get("kunst"):
        kunst_zeichnen(backend, rect, b["kunst"], breite * 96 / 72, rgba(b.get("farbe", SCHWARZ)))
        return
    zeichne_rahmen(backend, b.get("farbe", SCHWARZ), breite, b.get("art", "einfach"), b.get("seiten", "tblr"), rect, 96 / 72)
