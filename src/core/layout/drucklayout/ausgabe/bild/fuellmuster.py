"""Kacheln für Muster- und Texturfüllungen, ohne Qt: dieselben Bilder wie bisher (8 × 8-Muster aus Bayer-Matrix und Linienrichtungen; Texturen aus festem Zufallssamen),
als RGBA-Bytes. Die Zeichenflächen des Kerns füllen damit (Raster: abgetastet nach Benutzerkoordinaten, PDF: Kachelmuster)."""
from __future__ import annotations

import random

from core.layout.drucklayout.ausgabe.backend import rgba

_BAYER = ((0, 32, 8, 40, 2, 34, 10, 42), (48, 16, 56, 24, 50, 18, 58, 26), (12, 44, 4, 36, 14, 46, 6, 38), (60, 28, 52, 20, 62, 30, 54, 22),
          (3, 35, 11, 43, 1, 33, 9, 41), (51, 19, 59, 27, 49, 17, 57, 25), (15, 47, 7, 39, 13, 45, 5, 37), (63, 31, 55, 23, 61, 29, 53, 21))
_TEXTUR_BASIS = {"papier": "#f1ead8", "granit": "#9a9a9a", "holz": "#c8955a", "stoff": "#8aa4c8", "marmor": "#e6e6ea", "sand": "#e3cf9f"}
_KACHELN: dict = {}


def _farbe(text, standard):
    try:
        return rgba(text)
    except (ValueError, IndexError, TypeError, AttributeError):
        return standard


def muster_an(schluessel: str, x: int, y: int) -> bool:
    """Ist das Bildelement (x, y) der 8 × 8-Kachel in der Musterfarbe?"""
    if schluessel == "rein":
        return True
    if schluessel.startswith("pct"):
        p = float(schluessel[3:].replace("_", "."))
        return p * 64 / 100 > _BAYER[y][x]
    art, richtung = schluessel.split("_", 1)
    breit = 3 if art == "dunkel" else 1
    waag, senk = y < breit, x < breit
    ab, auf = (x - y) % 8 < breit, (x + y) % 8 < breit
    return {"h": waag, "v": senk, "ab": ab, "auf": auf, "raster": waag or senk, "karo": ab or auf}[richtung]


def muster_kachel(schluessel: str, farbe: str = "#000000", grund: str | None = None):
    """8 × 8-Kachel des Musters → ``(8, 8, [(r, g, b, a)] zeilenweise)``; ohne Grundfarbe bleibt der Grund durchsichtig."""
    k = ("m", schluessel, farbe, grund)
    if k not in _KACHELN:
        vorn = _farbe(farbe, (0, 0, 0, 255))
        hinten = _farbe(grund, (0, 0, 0, 0)) if grund else (0, 0, 0, 0)
        _KACHELN[k] = (8, 8, [vorn if schluessel != "loeschen" and muster_an(schluessel, x, y) else hinten for y in range(8) for x in range(8)])
    return _KACHELN[k]


def textur_kachel(name: str, groesse: int = 64):
    """Textur ``papier``, ``granit``, ``holz``, ``stoff``, ``marmor`` oder ``sand`` → ``(g, g, [(r, g, b, a)] zeilenweise)``."""
    k = ("t", name, groesse)
    if k in _KACHELN:
        return _KACHELN[k]
    rnd = random.Random(name)
    basis = rgba(_TEXTUR_BASIS.get(name, "#cccccc"))
    px = [basis] * (groesse * groesse)

    def setze(x, y, farbe):
        if 0 <= x < groesse and 0 <= y < groesse:
            px[y * groesse + x] = farbe
    for _ in range(groesse * 3):
        x, y = rnd.randrange(groesse), rnd.randrange(groesse)
        d = rnd.randint(-28, 28)
        c = (max(0, min(255, basis[0] + d)), max(0, min(255, basis[1] + d)), max(0, min(255, basis[2] + d)), 255)
        if name == "holz":
            steigung = rnd.randint(-1, 1)
            for xx in range(groesse):
                setze(xx, y + round(steigung * xx / groesse), c)
        elif name == "stoff":
            for t in range(groesse):
                setze(x, t, c)
                setze(t, y, c)
        else:
            setze(x, y, c)
    _KACHELN[k] = (groesse, groesse, px)
    return _KACHELN[k]


def kachel_von(fuellung):
    """Die Kachel zu einer ``PatternFill`` oder ``TextureFill`` des Backends."""
    from core.layout.drucklayout.ausgabe.backend import PatternFill
    if isinstance(fuellung, PatternFill):
        return muster_kachel(fuellung.key, fuellung.color, fuellung.ground)
    return textur_kachel(fuellung.key, 64)
