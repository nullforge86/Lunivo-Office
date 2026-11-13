"""Linienarten ohne Qt: einfach, gepunktet, gestrichelt, Strich-Punkt, doppelt, dreifach, Dünn-Dick-Folgen und Wellenlinien, als Zeichenanweisungen für ein ``RenderTarget``.

``STILE``: Schlüssel → (Name, Strichart, DOCX-Wert, Bahnen, wellig). Eine Bahn ist (Abstand von der Mitte, Dicke), beides in Linienbreiten; Mehrfachlinien sind mehrere Bahnen nebeneinander.
Die Strichart ist ``None`` (durchgezogen), ``"dot"``, ``"dash"``, ``"dashdot"``, ``"dashdotdot"`` oder ein Muster (Strich, Lücke, …) in Linienbreiten."""
from __future__ import annotations

import math

from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.rendering.backend import RenderTarget, Style, rgba


def _bauen() -> dict:
    a = {"einfach": ("Einfach", None, "single", [(0, 1.0)], False),
         "gepunktet": ("Gepunktet", "dot", "dotted", [(0, 1.0)], False),
         "fein_gestrichelt": ("Fein gestrichelt", (3.0, 2.0), "dashSmallGap", [(0, 1.0)], False),
         "gestrichelt": ("Gestrichelt", "dash", "dashed", [(0, 1.0)], False),
         "strichpunkt": ("Strich-Punkt", "dashdot", "dotDash", [(0, 1.0)], False),
         "strichpunktpunkt": ("Strich-Punkt-Punkt", "dashdotdot", "dotDotDash", [(0, 1.0)], False),
         "doppelt": ("Doppelt", None, "double", [(-1.0, 0.34), (1.0, 0.34)], False),
         "dreifach": ("Dreifach", None, "triple", [(-1.7, 0.3), (0, 0.3), (1.7, 0.3)], False)}
    for gross, name, wert in ((1.0, "eng", "Small"), (1.7, "mittel", "Medium"), (2.5, "weit", "Large")):
        spanne = 0.3 + gross + 1.0
        a[f"duenn_dick_{name}"] = (f"Dünn–dick ({name})", None, f"thinThick{wert}Gap", [(-spanne / 2 + 0.15, 0.3), (spanne / 2 - 0.5, 1.0)], False)
        a[f"dick_duenn_{name}"] = (f"Dick–dünn ({name})", None, f"thickThin{wert}Gap", [(-spanne / 2 + 0.5, 1.0), (spanne / 2 - 0.15, 0.3)], False)
        bis = 0.3 + gross + 1.0 + gross + 0.3
        a[f"duenn_dick_duenn_{name}"] = (f"Dünn–dick–dünn ({name})", None, f"thinThickThin{wert}Gap", [(-bis / 2 + 0.15, 0.3), (0, 1.0), (bis / 2 - 0.15, 0.3)], False)
    a["wellig"] = ("Wellenlinie", None, "wave", [(0, 1.0)], True)
    a["doppelwellig"] = ("Doppelte Wellenlinie", None, "doubleWave", [(-1.1, 0.45), (1.1, 0.45)], True)
    return a


STILE = _bauen()


def zeichne_linie(b: RenderTarget, farbe: str, breite_pt: float, art: str, x1: float, y1: float, x2: float, y2: float, massstab: float = 1.0) -> None:
    """Eine einzelne Linie in ihrer Art; ``massstab`` rechnet pt in Bildpunkte um (96/72 am Bildschirm, mal Zoom)."""
    _n, strich, _d, bahnen, wellig = STILE.get(art, STILE["einfach"])
    w = max(0.6, breite_pt * massstab)
    laenge = math.hypot(x2 - x1, y2 - y1)
    if laenge <= 0:
        return
    nx, ny = -(y2 - y1) / laenge, (x2 - x1) / laenge
    for versatz, dicke in bahnen:
        ox, oy = nx * versatz * w, ny * versatz * w
        stil = Style(color=rgba(farbe), width=max(0.6, w * dicke), dash=strich, cap="flat")
        if not wellig:
            b.draw_line(Point(x1 + ox, y1 + oy), Point(x2 + ox, y2 + oy), stil)
            continue
        amp, lam = max(1.2, w * 0.9), max(6.0, w * 6)                          # Wellenlinie: Sinus entlang der Linie
        ux, uy = (x2 - x1) / laenge, (y2 - y1) / laenge
        ops, t = [], 0.0
        while t <= laenge:
            d = amp * math.sin(2 * math.pi * t / lam)
            ops.append(("M" if not ops else "L", x1 + ox + ux * t + nx * d, y1 + oy + uy * t + ny * d))
            t += 1.0
        b.draw_path(ops, stil, antialias=None)


def zeichne_rahmen(b: RenderTarget, farbe: str, breite_pt: float, art: str, seiten: str, r: Rect, massstab: float = 1.0, innen_y=()) -> None:
    """Die gemeinten Seiten (``t``, ``b``, ``l``, ``r``; ``h`` = Linien zwischen Absätzen bei ``innen_y``) eines Rechtecks in der Linienart."""
    for kennz, (a, c) in (("t", ((r.x, r.y), (r.right, r.y))), ("b", ((r.x, r.bottom), (r.right, r.bottom))),
                          ("l", ((r.x, r.y), (r.x, r.bottom))), ("r", ((r.right, r.y), (r.right, r.bottom)))):
        if kennz in seiten:
            zeichne_linie(b, farbe, breite_pt, art, a[0], a[1], c[0], c[1], massstab)
    if "h" in seiten:
        for y in innen_y:
            zeichne_linie(b, farbe, breite_pt, art, r.x, y, r.right, y, massstab)


ALLE_SEITEN = "tblr"
RAHMEN_POLSTER = 4.0                                                   # Abstand des Absatzrahmens zum Text in Bildpunkten, wenn die Angabe keinen nennt
PX_JE_PT = 96.0 / 72.0


def rahmen_aus_text(text: str | None) -> tuple[str, float, str, str, tuple[float, float, float, float] | None] | None:
    """Die Rahmenangabe eines Absatzes „Farbe|Breite pt|Art|Seiten|oben,unten,links,rechts“ → (Farbe, Breite pt, Art, Seiten, Abstände pt oder ``None``)."""
    if not text:
        return None
    t = text.split("|")
    try:
        breite = float(t[1]) if len(t) > 1 and t[1] else 1.0
        abstand = tuple(float(x) for x in t[4].split(",")) if len(t) > 4 and t[4] else None
    except ValueError:
        return None
    return t[0] or "#000000", breite, t[2] if len(t) > 2 and t[2] else "einfach", t[3] if len(t) > 3 else ALLE_SEITEN, abstand if abstand and len(abstand) == 4 else None


def zeichne_absatzrahmen(b: RenderTarget, text: str, flaeche: Rect, innen_y=()) -> None:
    """Der Rahmen um die Fläche zusammenhängender Absätze (``flaeche`` = ihre Zeilen auf der Seite), mit dem Abstand der Angabe zum Text."""
    angabe = rahmen_aus_text(text)
    if angabe is None:
        return
    farbe, breite, art, seiten, abstand = angabe
    if abstand:
        o, u, l, r = (x * PX_JE_PT for x in abstand)
        rect = Rect(flaeche.x - l, flaeche.y - o, flaeche.width + l + r, flaeche.height + o + u)
    else:
        pd = RAHMEN_POLSTER
        rect = Rect(flaeche.x - pd, flaeche.y - pd + 1, flaeche.width + 2 * pd, flaeche.height + 2 * pd - 2)
    zeichne_rahmen(b, farbe, breite, art, seiten, rect, PX_JE_PT, innen_y)
