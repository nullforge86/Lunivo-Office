"""Lage von Bildern und Formen auf dem Blatt, ohne Qt: aus Verankerung und Größe das Rechteck in Blattkoordinaten (Ursprung links oben, Bildpunkte)."""
from __future__ import annotations

from lunivo_writer.core.document.objekte import Anchor
from lunivo_writer.core.geometry import Rect


def objekt_rechteck(anker: Anchor, b: float, h: float, blatt_b: float, blatt_h: float, ml: float, mt: float, inhalt_b: float, inhalt_h: float,
                    absatz_y: float = 0.0, spalte_x: float | None = None, seite: int = 1) -> Rect:
    """Das Rechteck des Objekts auf dem Blatt. ``absatz_y``: oberer Rand des Absatzes (Blattkoordinate), ``spalte_x``: linker Rand der Spalte,
    ``seite``: Seitennummer (innen/außen: auf Seiten mit ungerader Nummer liegt innen links)."""
    x0, bw = {"seite": (0.0, blatt_b), "rand": (ml, inhalt_b)}.get(anker.h_ref, (ml if spalte_x is None else spalte_x, inhalt_b))
    al = anker.h_align
    if al in ("inside", "outside"):
        al = "left" if (al == "inside") == (seite % 2 == 1) else "right"
    if al == "center":
        x = x0 + (bw - b) / 2
    elif al == "right":
        x = x0 + bw - b
    elif al == "left":
        x = x0
    else:
        x = x0 + anker.x
    y0, bh = {"seite": (0.0, blatt_h), "rand": (mt, inhalt_h)}.get(anker.v_ref, (absatz_y, 0.0))
    av = anker.v_align
    if av == "center":
        y = y0 + (bh - h) / 2
    elif av == "bottom":
        y = y0 + bh - h
    elif av == "top" and anker.v_ref != "absatz":
        y = y0
    else:
        y = y0 + anker.y
    return Rect(x, y, b, h)
