"""Diagramme (Säulen, Balken, Linien, Flächen, Kreis) über das Rendering-Backend zeichnen — ohne Qt.

``d`` = {"art", "titel", "kategorien", "reihen" {Name: [Werte]}, "farben" [#rrggbb], "legende", "wert" {min, max, intervall, stellen}, "luecke", "rubrikenraster"}.
Die Lage kommt vom Layoutkern; hier wird nur gezeichnet. Maße in Bildpunkten (96 dpi)."""
from __future__ import annotations

import math

from ..geometry import Point, Rect
from ..textlayout.engine import FontSpec
from .backend import Style, rgba

_FARBEN = ("#4472c4", "#ed7d31", "#a5a5a5", "#ffc000", "#5b9bd5", "#70ad47", "#264478", "#9e480e")
_SCHRIFT = "Liberation Sans"
_TEXT = (38, 38, 38, 255)
_RASTER = (217, 217, 217, 255)
_ACHSE = (134, 134, 134, 255)


def _breite(b, text: str, font) -> float:
    return b.text_bounds(text, Rect(0, 0, 2000, 200), font, "left", False).width


def _zahl(wert: float, stellen: int) -> str:
    return f"{wert:.{stellen}f}".replace(".", ",") if stellen else str(int(round(wert)))


def _schritt(spanne: float) -> float:
    """Hauptintervall: etwa zehn Teilstriche, auf 1, 2 oder 5 mal Zehnerpotenz."""
    roh = spanne / 10.0 if spanne > 0 else 1.0
    exp = math.floor(math.log10(roh))
    for faktor in (1, 2, 5, 10):
        if faktor * 10 ** exp >= roh:
            return faktor * 10 ** exp
    return 10 ** (exp + 1)


def _skala(d: dict, werte: list[float], gestapelt: str) -> tuple[float, float, float]:
    """(Minimum, Maximum, Intervall) der Wertachse: Angaben der Datei, sonst wie Word."""
    w = d.get("wert") or {}
    if gestapelt == "prozent":
        lo, hi = 0.0, 1.0
        schritt = w.get("intervall") or 0.1
    else:
        lo = w.get("min") if w.get("min") is not None else min(0.0, min(werte, default=0.0))
        spitze = max(werte, default=1.0)
        schritt = w.get("intervall") or _schritt(max(spitze * 1.05 - lo, 1e-9))
        hi = w.get("max") if w.get("max") is not None else (math.ceil((spitze * 1.05 if spitze > 0 else 1.0) / schritt - 1e-9) * schritt)
    if hi <= lo:
        hi = lo + schritt
    return lo, hi, schritt


def zeichne_diagramm(b, r: Rect, d: dict) -> None:
    art = str(d.get("art") or "saeule_gruppiert")
    b.draw_rect(r, Style(color=(255, 255, 255, 255), width=0, filled=True))
    b.draw_rect(Rect(r.x + 0.5, r.y + 0.5, r.width - 1, r.height - 1), Style(color=_RASTER, width=1))
    reihen = {k: list(v) for k, v in (d.get("reihen") or {}).items()}
    kat = list(d.get("kategorien") or [])
    if not reihen or not kat:
        return
    namen = list(reihen)
    farben = [rgba(f) for f in (d.get("farben") or [])] + [rgba(f) for f in _FARBEN]
    schrift = FontSpec(_SCHRIFT, 9.5)
    kopf = 8.0
    if d.get("titel_an") and d.get("titel"):
        tf = FontSpec(_SCHRIFT, 12.0, 400)
        b.draw_text_box(str(d["titel"]), Rect(r.x, r.y + 4, r.width, 22), tf, Style(color=(64, 64, 64, 255)), "center", False, "top")
        kopf = 30.0
    fuss = 0.0
    if art.startswith("kreis") or art == "ring":
        _kreis(b, Rect(r.x + 8, r.y + kopf, r.width - 16, r.height - kopf - (24 if d.get("legende") else 8)), kat, reihen[namen[0]], farben, art == "ring")
        if d.get("legende"):
            _legende(b, r, kat, farben, schrift)
        return
    if d.get("legende"):
        fuss = 24.0
    gestapelt = "prozent" if art.endswith("_100") else "ja" if art.endswith("_gestapelt") else ""
    waagerecht = art.startswith("balken")
    werte_alle = [w for v in reihen.values() for w in v]
    if gestapelt:
        summen = [sum(reihen[n][i] if i < len(reihen[n]) else 0.0 for n in namen) for i in range(len(kat))]
        werte_skala = summen if gestapelt == "ja" else [1.0]
    else:
        werte_skala = werte_alle
    lo, hi, schritt = _skala(d, werte_skala, gestapelt)
    stellen = int((d.get("wert") or {}).get("stellen") or 0)
    marken = []
    n = int(round((hi - lo) / schritt)) if schritt > 0 else 1
    for i in range(max(1, n) + 1):
        marken.append(lo + i * schritt)
    beschr = [(_zahl(m * 100, 0) + " %") if gestapelt == "prozent" else _zahl(m, stellen) for m in marken]
    breit_max = max((_breite(b, t, schrift) for t in beschr), default=10.0)
    kat_breit = max((_breite(b, str(k), schrift) for k in kat), default=10.0)
    if waagerecht:
        links = 8.0 + kat_breit + 6
        unten = 8.0 + 14 + 4 + fuss
    else:
        links = 8.0 + breit_max + 6
        unten = 8.0 + 14 + 4 + fuss
    p = Rect(r.x + links, r.y + kopf + (4 if not waagerecht else 4), r.width - links - 14, r.height - kopf - unten - 4)
    if p.width < 20 or p.height < 20:
        return
    linie = Style(color=_RASTER, width=1)
    achse = Style(color=_ACHSE, width=1)
    ntxt = Style(color=_TEXT)

    def pos(wert: float) -> float:
        return (wert - lo) / (hi - lo)

    # Raster und Beschriftung der Wertachse
    for m, t in zip(marken, beschr):
        a = pos(m)
        if waagerecht:
            x = p.x + a * p.width
            b.draw_line(Point(x, p.y), Point(x, p.bottom), linie)
            b.draw_text_box(t, Rect(x - 25, p.bottom + 4, 50, 14), schrift, ntxt, "center", False, "top")
        else:
            y = p.bottom - a * p.height
            b.draw_line(Point(p.x, y), Point(p.right, y), linie)
            b.draw_text_box(t, Rect(r.x + 6, y - 7, links - 12, 14), schrift, ntxt, "right", False, "center")
    anzahl = len(kat)
    gruppe = (p.height if waagerecht else p.width) / anzahl
    luecke = float(d.get("luecke") if d.get("luecke") is not None else 150.0) / 100.0
    for i, k in enumerate(kat):                                                      # Rubriken
        mitte = (p.bottom - (i + 0.5) * gruppe) if waagerecht else (p.x + (i + 0.5) * gruppe)
        if waagerecht:
            b.draw_text_box(str(k), Rect(r.x + 6, mitte - 7, links - 12, 14), schrift, ntxt, "right", False, "center")
        else:
            b.draw_text_box(str(k), Rect(mitte - gruppe / 2, p.bottom + 4, gruppe, 14), schrift, ntxt, "center", False, "top")
    if art.startswith("saeule") or waagerecht:
        _balken(b, p, kat, reihen, namen, farben, gestapelt, waagerecht, gruppe, luecke, lo, hi, pos)
    elif art.startswith("linie") or art.startswith("flaeche"):
        _linien(b, p, kat, reihen, namen, farben, gestapelt, art.startswith("flaeche"), gruppe, pos)
    if waagerecht:
        b.draw_line(Point(p.x, p.y), Point(p.x, p.bottom), achse)
    else:
        b.draw_line(Point(p.x, p.bottom), Point(p.right, p.bottom), achse)
        b.draw_line(Point(p.x, p.y), Point(p.x, p.bottom), achse)
    if d.get("legende"):
        _legende(b, r, namen, farben, schrift)


def _balken(b, p, kat, reihen, namen, farben, gestapelt, waagerecht, gruppe, luecke, lo, hi, pos) -> None:
    n = len(namen)
    breite = gruppe / ((1 if gestapelt else n) + luecke)
    for i in range(len(kat)):
        summe = sum(reihen[nm][i] if i < len(reihen[nm]) else 0.0 for nm in namen) or 1.0
        stapel = 0.0
        for s, nm in enumerate(namen):
            w = reihen[nm][i] if i < len(reihen[nm]) else 0.0
            if gestapelt == "prozent":
                w = w / summe
            von, bis = (stapel, stapel + w) if gestapelt else (max(lo, 0.0), w)
            if gestapelt:
                stapel += w
            a0, a1 = pos(min(von, bis)), pos(max(von, bis))
            versatz = ((gruppe - breite * (1 if gestapelt else n)) / 2) + (0 if gestapelt else s * breite)
            if waagerecht:
                y = p.bottom - i * gruppe - versatz - breite
                rect = Rect(p.x + a0 * p.width, y, (a1 - a0) * p.width, breite)
            else:
                x = p.x + i * gruppe + versatz
                rect = Rect(x, p.bottom - a1 * p.height, breite, (a1 - a0) * p.height)
            b.draw_rect(rect, Style(color=farben[s % len(farben)], width=0, filled=True))


def _linien(b, p, kat, reihen, namen, farben, gestapelt, flaeche, gruppe, pos) -> None:
    anzahl = len(kat)
    unten = [0.0] * anzahl
    for s, nm in enumerate(namen):
        werte = [reihen[nm][i] if i < len(reihen[nm]) else 0.0 for i in range(anzahl)]
        if gestapelt == "prozent":
            summen = [sum(reihen[n][i] if i < len(reihen[n]) else 0.0 for n in namen) or 1.0 for i in range(anzahl)]
            werte = [w / sm for w, sm in zip(werte, summen)]
        oben = [u + w for u, w in zip(unten, werte)] if gestapelt else werte
        pts = [Point(p.x + (i + 0.5) * gruppe, p.bottom - pos(o) * p.height) for i, o in enumerate(oben)]
        farbe = farben[s % len(farben)]
        if flaeche:
            ops = [("M", pts[0].x, p.bottom - pos(unten[0] if gestapelt else 0.0) * p.height)] + [("L", q.x, q.y) for q in pts]
            ops += [("L", pts[-1].x, p.bottom - pos(unten[-1] if gestapelt else 0.0) * p.height), ("Z",)]
            b.draw_path(ops, Style(color=(farbe[0], farbe[1], farbe[2], 190), width=0, filled=True))
        for q0, q1 in zip(pts, pts[1:]):
            b.draw_line(q0, q1, Style(color=farbe, width=2.5, cap="round"))
        if gestapelt:
            unten = oben


def _kreis(b, r: Rect, kat, werte, farben, ring: bool) -> None:
    summe = sum(w for w in werte if w > 0) or 1.0
    radius = min(r.width, r.height) / 2 - 2
    mx, my = r.x + r.width / 2, r.y + r.height / 2
    winkel = -math.pi / 2
    for i, w in enumerate(werte):
        if w <= 0:
            continue
        schritt = 2 * math.pi * w / summe
        n = max(2, int(schritt / math.radians(3)) + 1)
        ops = [("M", mx, my)] + [("L", mx + radius * math.cos(winkel + schritt * k / n), my + radius * math.sin(winkel + schritt * k / n)) for k in range(n + 1)] + [("Z",)]
        b.draw_path(ops, Style(color=farben[i % len(farben)], width=1, filled=True, outline=(255, 255, 255, 255)))
        winkel += schritt
    if ring:
        b.draw_ellipse(Point(mx, my), radius * 0.5, radius * 0.5, Style(color=(255, 255, 255, 255), width=0, filled=True))


def _legende(b, r: Rect, namen, farben, schrift) -> None:
    breiten = [_breite(b, str(n), schrift) + 22 for n in namen]
    x = r.x + (r.width - sum(breiten)) / 2
    y = r.bottom - 20
    for i, n in enumerate(namen):
        b.draw_rect(Rect(x, y + 4, 8, 8), Style(color=farben[i % len(farben)], width=0, filled=True))
        b.draw_text_box(str(n), Rect(x + 12, y, breiten[i] - 12, 16), schrift, Style(color=_TEXT), "left", False, "center")
        x += breiten[i]
