"""Zeichenzusätze am Text ohne Qt: Unterstreichungsarten, doppelt Durchgestrichenes, Betonungszeichen, umschlossene Zeichen und Leittext (Ruby), gezeichnet auf eine ``RenderTarget``.

Maße in Bildpunkten; ``grundlinie`` ist die y-Koordinate der Schriftlinie, ``groesse`` die Schriftgröße in Bildpunkten."""
from __future__ import annotations

import math

from lunivo_writer.kern.geometrie import Point, Rect
from .backend import Style

# Strichmuster der Unterstreichungen (in Linienbreiten) und ob sie dick (Faktor) oder wellig sind
UNTER_MUSTER = {"einfach": ([], 1, False), "gepunktet": ([1.0, 1.0], 1, False), "gestrichelt": ([3.0, 2.0], 1, False),
                "strichpunkt": ([4.0, 2.0, 1.0, 2.0], 1, False), "strichpunktpunkt": ([4.0, 2.0, 1.0, 2.0, 1.0, 2.0], 1, False),
                "wellig": ([], 1, True), "woerter": ([], 1, False), "doppelt": ([], 1, False), "dick": ([], 2, False), "dick_gepunktet": ([1.0, 1.0], 2, False),
                "dick_gestrichelt": ([3.0, 2.0], 2, False), "lang": ([7.0, 3.0], 1, False), "dick_lang": ([7.0, 3.0], 2, False),
                "dick_strichpunkt": ([4.0, 2.0, 1.0, 2.0], 2, False), "dick_strichpunktpunkt": ([4.0, 2.0, 1.0, 2.0, 1.0, 2.0], 2, False),
                "dick_wellig": ([], 2, True), "doppelwellig": ([], 1, True)}


def unterstrich(b, strecken: list, art: str, grundlinie: float, groesse: float, farbe: tuple) -> None:
    """Unterstreichungen: einfach, doppelt, dick, lang gestrichelt, gepunktet, Wellen in zwei Stärken; ``strecken`` = [(x0, x1)]."""
    muster, dicke, wellig = UNTER_MUSTER.get(art, ([], 1, False))
    w = max(1.0, groesse * 0.05) * dicke
    y = grundlinie + max(1.5, groesse * 0.12)
    stil = Style(color=farbe, width=w, dash=tuple(muster) if muster else None, cap="flat")
    for x0, x1 in strecken:
        if x1 <= x0:
            continue
        for yy in ((y, y + w * 2.2) if art == "doppelt" else (y,)):
            if wellig:
                ops = [("M", x0, yy)]
                x, rich, schritt = x0, 1, max(2.0, groesse * 0.12)
                while x < x1:
                    ops.append(("Q", x + schritt / 2, yy + rich * schritt * 0.5, min(x + schritt, x1), yy))
                    x += schritt
                    rich = -rich
                b.draw_path(ops, stil, True, True)
                if art == "doppelwellig":
                    b.draw_path([(op[0],) + tuple(v + (w * 2.6 if i % 2 == 0 else 0.0) for i, v in enumerate(op[1:])) for op in ops], stil, True, True)
            else:
                b.draw_line(Point(x0, yy), Point(x1, yy), stil)


def doppelt_durch(b, rect: Rect, grundlinie: float, groesse: float, farbe: tuple) -> None:
    """Die zweite Durchstreichlinie: zwei Linien in Höhe der Kleinbuchstaben."""
    for dy in (0.26, 0.38):
        y = grundlinie - groesse * dy
        b.draw_line(Point(rect.x, y), Point(rect.x + rect.width, y), Style(color=farbe, width=max(1.0, groesse * 0.05)))


def betonung(b, glyphen: list, art: str, grundlinie: float, groesse: float, farbe: tuple) -> None:
    """Betonungszeichen: ein Punkt, Kreis oder Komma über (oder ein Punkt unter) jedem Buchstaben; ``glyphen`` = [(x, oben, unten)]."""
    r = max(1.2, groesse * 0.065)
    for x, oben, unten in glyphen:
        if art == "unten":
            b.draw_ellipse(Point(x, max(unten, grundlinie) + r * 2.2), r, r, Style(color=farbe, width=0, filled=True))
            continue
        y = oben - r * 2.2
        if art == "kreis":
            b.draw_ellipse(Point(x, y), r, r, Style(color=farbe, width=max(0.8, r * 0.5)))
        elif art == "komma":
            b.draw_ellipse(Point(x, y), r, r, Style(color=farbe, width=0, filled=True))
            b.draw_line(Point(x + r * 0.6, y + r * 0.4), Point(x - r * 0.4, y + r * 2.0), Style(color=farbe, width=max(0.8, r * 0.6)))
        else:
            b.draw_ellipse(Point(x, y), r, r, Style(color=farbe, width=0, filled=True))


def umschlossen(b, kasten: Rect, wie: tuple, farbe: tuple, groesse: float) -> None:
    """Die Form um die Zeichen: „reduzieren“ legt sie eng an, „erweitern“ lässt dem Symbol Raum."""
    form, vorlage = wie
    rand = groesse * (0.08 if vorlage == "reduzieren" else 0.22)
    x, y, w, h = kasten.x - rand, kasten.y, kasten.width + 2 * rand, kasten.height
    if form in ("kreis", "raute"):
        x, w = x - groesse * 0.1, w + 2 * groesse * 0.1
    stil = Style(color=farbe, width=max(0.6, groesse * 0.06))
    cx, cy = x + w / 2, y + h / 2
    if form == "kreis":
        b.draw_ellipse(Point(cx, cy), w / 2, h / 2, stil)
    elif form == "quadrat":
        b.draw_rect(Rect(x, y, w, h), stil)
    elif form == "dreieck":
        b.draw_path([("M", cx, y), ("L", x + w, y + h), ("L", x, y + h), ("Z",)], stil, True, True)
    else:
        b.draw_path([("M", cx, y), ("L", x + w, cy), ("L", cx, y + h), ("L", x, cy), ("Z",)], stil, True, True)


def ruby(b, engine, x0: float, x1: float, grundlinie: float, groesse: float, ruby_: dict, farbe: tuple, familie: str = "Liberation Sans") -> None:
    """Der Leittext über dem Basistext, in kleinerer Schrift, nach der gewählten Ausrichtung."""
    from lunivo_writer.kern.textsatz.engine import FontSpec
    PX = 96.0 / 72.0
    f = FontSpec(familie, max(4, int(ruby_["groesse"] * PX)) * 72.0 / 96.0)
    text = ruby_["ruby"]
    breite = engine.measure_text(text, f)
    y = grundlinie - groesse * 0.95 - ruby_["abstand"] * PX
    if ruby_["ausrichtung"] == "links":
        x = x0
    elif ruby_["ausrichtung"] == "rechts":
        x = x1 - breite
    else:
        x = (x0 + x1 - breite) / 2
    stil = Style(color=farbe)
    if ruby_["ausrichtung"] == "verteilt" and len(text) > 1 and x1 - x0 > breite:
        schritt = (x1 - x0 - breite) / (len(text) - 1)
        for i, ch in enumerate(text):
            b.draw_text(ch, Point(x0 + engine.measure_text(text[:i], f) + schritt * i, y), f, stil)
    else:
        b.draw_text(text, Point(max(x0, x) if breite < x1 - x0 else x, y), f, stil)
