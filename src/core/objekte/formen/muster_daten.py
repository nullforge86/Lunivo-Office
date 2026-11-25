"""Muster daten: aus ``vcl.qt.rendering.formen.muster`` herausgelöst."""
from __future__ import annotations
from core.formatierung.farben.farben import Farbe
from core.dokument.musterschluessel import MUSTER


_BAYER = ((0, 32, 8, 40, 2, 34, 10, 42), (48, 16, 56, 24, 50, 18, 58, 26), (12, 44, 4, 36, 14, 46, 6, 38), (60, 28, 52, 20, 62, 30, 54, 22),
          (3, 35, 11, 43, 1, 33, 9, 41), (51, 19, 59, 27, 49, 17, 57, 25), (15, 47, 7, 39, 13, 45, 5, 37), (63, 31, 55, 23, 61, 29, 53, 21))


_NAME = {k: n for k, n, _o in MUSTER}


_OOXML = {k: o for k, _n, o in MUSTER}


_VON_OOXML = {o: k for k, _n, o in MUSTER}


def name_von(schluessel: str) -> str:
    return _NAME.get(schluessel, schluessel)


def ooxml_von(schluessel: str) -> str:
    return _OOXML.get(schluessel, "clear")


def schluessel_von_ooxml(wert: str | None) -> str | None:
    return _VON_OOXML.get(wert or "")


def _an(schluessel: str, x: int, y: int) -> bool:
    """Ist das Bildelement (x, y) der 8 × 8-Kachel in der Musterfarbe?"""
    if schluessel == "rein":
        return True
    if schluessel.startswith("pct"):
        p = float(schluessel[3:].replace("_", "."))
        return p * 64 / 100 > _BAYER[y][x]
    art, richtung = schluessel.split("_", 1)
    dick = art == "dunkel"
    breit = 3 if dick else 1
    waag, senk = y < breit, x < breit
    ab, auf = (x - y) % 8 < breit, (x + y) % 8 < breit
    return {"h": waag, "v": senk, "ab": ab, "auf": auf, "raster": waag or senk, "karo": ab or auf}[richtung]


def als_text(schluessel: str, muster: str, fuell: str | None) -> str:
    return f"{schluessel}|{muster}|{fuell or ''}"


def aus_text(text: str | None) -> tuple[str, str, str | None] | None:
    if not text:
        return None
    t = text.split("|")
    if len(t) < 2 or not t[0] or t[0] not in _NAME:
        return None
    return t[0], t[1] or Farbe.SCHWARZ, (t[2] if len(t) > 2 and t[2] else None)
