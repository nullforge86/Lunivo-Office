"""Lage frei positionierter Objekte auf dem Blatt, ohne Qt: aus Verankerung und Größe das Rechteck in Blattkoordinaten (Ursprung links oben, Bildpunkte)."""
from __future__ import annotations

from lunivo_writer.core.document.dokument import FreiesObjekt
from lunivo_writer.core.geometry import Rect

UMBRUCH_MIT_UMFLUSS = ("quadrat", "eng", "oben_unten")      # Text weicht dem Objekt aus
OBJEKT_ABSTAND = 6.0                                        # Abstand zwischen Objekt und umfließendem Text


def objekt_rechteck(o: FreiesObjekt, blatt_b: float, blatt_h: float, ml: float, mt: float, inhalt_b: float, inhalt_h: float,
                    absatz_y: float = 0.0, spalte_x: float | None = None, seite: int = 1, spalte_b: float | None = None) -> Rect:
    """Das Rechteck des Objekts auf dem Blatt. ``absatz_y``: oberer Rand des Ankerabsatzes (Blattkoordinate), ``spalte_x`` und ``spalte_b``:
    linker Rand und Breite der Spalte, ``seite``: angezeigte Seitennummer (innen/außen: auf Seiten mit ungerader Nummer liegt innen links)."""
    x0, bw = {"seite": (0.0, blatt_b), "rand": (ml, inhalt_b)}.get(
        o.bezug_h, (ml if spalte_x is None else spalte_x, inhalt_b if spalte_b is None else spalte_b))
    al = o.ausr_h
    if al in ("inside", "outside"):
        al = "left" if (al == "inside") == (seite % 2 == 1) else "right"
    if al == "center":
        x = x0 + (bw - o.breite) / 2
    elif al == "right":
        x = x0 + bw - o.breite
    elif al == "left":
        x = x0
    else:
        x = x0 + o.x
    y0, bh = {"seite": (0.0, blatt_h), "rand": (mt, inhalt_h)}.get(o.bezug_v, (absatz_y, 0.0))
    av = o.ausr_v
    if av == "center":
        y = y0 + (bh - o.hoehe) / 2
    elif av == "bottom":
        y = y0 + bh - o.hoehe
    elif av == "top" and o.bezug_v != "absatz":
        y = y0
    else:
        y = y0 + o.y
    return Rect(x, y, o.breite, o.hoehe)
