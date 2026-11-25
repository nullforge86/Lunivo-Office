"""Füllung und Rahmen von Tabellenzellen und Textrahmen des Dokumentmodells, ohne Qt: aus den Formaten (``core/document/formate.py``) entstehen
Zeichenanweisungen für ein ``RenderTarget``.

Eine Kante der Zelle (``rahmen_oben`` …) und der Rahmen der Tabelle (``rahmen``) tragen die Angabe „Farbe|Breite pt|Art“ (Art wie in ``linien.STILE``);
„keine“ unterdrückt die Kante. Ohne eigene Angabe gilt der Tabellenrahmen (``rahmen_breite`` in Bildpunkten, ``rahmen_farbe``, ``rahmen_art``).
"""
from __future__ import annotations

from core.geometrie import Rect
from core.layout.drucklayout.ausgabe.backend import RenderTarget, Style, rgba
from core.layout.drucklayout.ausgabe.objekte.linien import STILE, zeichne_linie

PX_JE_PT = 96.0 / 72.0
KANTEN = (("oben", "t"), ("links", "l"), ("unten", "b"), ("rechts", "r"))
KEIN = "keine"


def _fuellung(text) -> tuple | None:
    return rgba(text) if isinstance(text, str) and text.startswith("#") else None


def _kante(angabe) -> tuple | None:
    """(Farbe, Breite in Bildpunkten, Art) einer Kantenangabe „Farbe|Breite pt|Art“; ``None`` ohne gültige Angabe."""
    if not isinstance(angabe, str) or not angabe or angabe == KEIN:
        return None
    t = angabe.split("|")
    try:
        breite = float(t[1]) * PX_JE_PT if len(t) > 1 and t[1] else 1.0 * PX_JE_PT
    except ValueError:
        return None
    art = t[2] if len(t) > 2 and t[2] in STILE else "einfach"
    return (t[0] or "#000000"), breite, art


def _linie(b: RenderTarget, k: str, r: Rect, farbe: str, breite: float, art: str) -> None:
    x1, y1, x2, y2 = {"t": (r.x, r.y, r.right, r.y), "b": (r.x, r.bottom, r.right, r.bottom),
                      "l": (r.x, r.y, r.x, r.bottom), "r": (r.right, r.y, r.right, r.bottom)}[k]
    zeichne_linie(b, farbe, breite / PX_JE_PT, art, x1, y1, x2, y2, PX_JE_PT)


def zeichne_zelle(b: RenderTarget, rect: Rect, zelle: dict, tabelle: dict) -> None:
    """Füllung und Rahmen einer Zelle auf dem Blatt (``rect``); ``zelle`` und ``tabelle`` sind die Formate."""
    fuell = _fuellung(zelle.get("hintergrund")) or _fuellung(tabelle.get("hintergrund"))
    if fuell is not None:
        b.draw_rect(rect, Style(color=fuell, width=0, filled=True))
    rand = float(tabelle.get("rahmen_breite") or 0.0)
    for name, k in KANTEN:
        eigen = zelle.get(f"rahmen_{name}")
        if eigen is not None:
            kante = _kante(eigen)
        elif rand > 0 and tabelle.get("rahmen_art") != KEIN:
            kante = (tabelle.get("rahmen_farbe") or "#000000", max(1.0, rand), tabelle.get("rahmen_art") if tabelle.get("rahmen_art") in STILE else "einfach")
        else:
            kante = None
        if kante is not None:
            _linie(b, k, rect, kante[0], kante[1], kante[2])
    diagonal = _kante(zelle.get("rahmen_diagonal"))
    if diagonal is not None:
        zeichne_linie(b, diagonal[0], diagonal[1] / PX_JE_PT, diagonal[2], rect.x, rect.y, rect.right, rect.bottom, PX_JE_PT)


def zeichne_textrahmen(b: RenderTarget, rect: Rect, rahmen: dict) -> None:
    """Füllung und Rahmenstrich eines Textrahmens im Text (``rahmen``: sein Format)."""
    fuell = _fuellung(rahmen.get("hintergrund"))
    if fuell is not None:
        b.draw_rect(rect, Style(color=fuell, width=0, filled=True))
    breite = float(rahmen.get("rahmen_breite") or 0.0)
    if breite > 0 and rahmen.get("rahmen_stil", 1) != 0:
        for _name, k in KANTEN:
            _linie(b, k, rect, rahmen.get("rahmen_farbe") or "#000000", max(1.0, breite), "einfach")
