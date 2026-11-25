"""Sprechblasen (Kommentarkarten im Seitenrand) ohne Qt: Messen und Zeichnen mit der Textsatz-Engine; Anzeige und Druck benutzen dieselben Funktionen.

Maße in Bildpunkten. Farben als ``(r, g, b, a)``; ``farben`` = (Karte, Rand, Text) — die Oberfläche liefert die Farben ihres Designs, der Druck immer helle."""
from __future__ import annotations

from core.geometrie import Point, Rect
from core.textsatz.engine import FontSpec
from core.layout.drucklayout.ausgabe.backend import Style

KOPF_HOEHE = 24.0                                  # die Kopfzeile: Kreis mit Initial, Name, Datum, Menüzeichen
_KAPPA = 0.5522847498
SCHATTEN_DECKKRAFT = 45                            # weicher Schatten der Karte
SCHATTEN_WEICH = 3.0
SCHATTEN_VERSATZ = 1.5
LINIE_BREITE = 1.4                                  # Verbindungslinie zum Text
ANKER_RADIUS = 2.6                                  # Ankerpunkt am Textende


def zeilen(engine, text: str, font: FontSpec, breite: float) -> list[str]:
    """Der Text in Zeilen der Breite ``breite`` (Absätze bleiben, Wörter brechen um)."""
    aus = []
    for absatz in (text or " ").split("\n"):
        if not absatz:
            aus.append("")
            continue
        for box in engine.layout_paragraph(absatz, font, max(1.0, breite)):
            aus.append(absatz[box.start:box.start + box.length].rstrip())
    return aus or [""]


def messen(engine, text: str, breite: float, font: FontSpec) -> float:
    """Höhe der Blase bei gegebener Breite."""
    innen = max(10.0, breite - 16)
    return 8 + KOPF_HOEHE + 6 + len(zeilen(engine, text, font, innen)) * engine.font_metrics(font).line_spacing + 8


def _rund(x: float, y: float, w: float, h: float, rad: float) -> list:
    k, r, b = rad * _KAPPA, x + w, y + h
    return [("M", x + rad, y), ("L", r - rad, y), ("C", r - rad + k, y, r, y + rad - k, r, y + rad), ("L", r, b - rad), ("C", r, b - rad + k, r - rad + k, b, r - rad, b),
            ("L", x + rad, b), ("C", x + rad - k, b, x, b - rad + k, x, b - rad), ("L", x, y + rad), ("C", x, y + rad - k, x + rad - k, y, x + rad, y), ("Z",)]


def zeichne_blase(b, engine, autor: str, datum: str, farbe: tuple, text: str, r: Rect, font: FontSpec, farben: tuple) -> None:
    """Eine Blase zeichnen wie eine Karte: Kreis mit Initial, Name fett, Datum, Menüzeichen, darunter der Text."""
    karte, rand, schrift = farben
    form = _rund(r.x, r.y, r.width, r.height, 8)
    b.draw_shadow(form, (0, 0, 0, SCHATTEN_DECKKRAFT), SCHATTEN_WEICH, 0.0, SCHATTEN_VERSATZ)          # weicher Schatten: die Karte hebt sich vom Blatt ab
    b.draw_path(form, Style(color=karte, width=1.0, filled=True, outline=rand), True, False)
    d = KOPF_HOEHE
    kx, ky = r.x + 8, r.y + 8
    b.draw_ellipse(Point(kx + d / 2, ky + d / 2), d / 2, d / 2, Style(color=farbe, width=0, filled=True))
    fett = FontSpec(font.family, font.size_pt, 700, font.italic)
    mf = engine.font_metrics(fett)
    base = ky + d / 2 + (mf.ascent - mf.descent) / 2                      # senkrecht zentriert in der Kopfzeile
    initial = ((autor or "?").strip()[:1] or "?").upper()
    b.draw_text(initial, Point(kx + d / 2 - engine.measure_text(initial, fett) / 2, base), fett, Style(color=(255, 255, 255, 255)))
    name = autor or "Unbekannt"
    b.draw_text(name, Point(kx + d + 8, base), fett, Style(color=schrift))
    klein = FontSpec(font.family, font.size_pt * 0.8, 400, font.italic)
    menue_x = r.x + r.width - 20
    frei = menue_x - 10 - (kx + d + 8 + engine.measure_text(name, fett) + 10)         # so viel Platz bleibt neben dem Namen für das Datum
    for kandidat in (datum, datum[11:], ""):                                          # vollständig, nur die Uhrzeit, sonst gar nicht (nie über den Namen)
        if engine.measure_text(kandidat, klein) <= frei:
            datum = kandidat
            break
    kf = engine.font_metrics(klein)
    b.draw_text(datum, Point(menue_x - 10 - engine.measure_text(datum, klein), ky + d / 2 + (kf.ascent - kf.descent) / 2), klein, Style(color=rand))
    for i in range(3):                                                                # das „☰“ rechts
        y = r.y + 8 + d / 2 - 4 + i * 4
        b.draw_line(Point(menue_x, y), Point(menue_x + 10, y), Style(color=rand, width=1.4, cap="round"))
    f = FontSpec(font.family, font.size_pt, 400, font.italic)
    m = engine.font_metrics(f)
    y = r.y + 8 + d + 6
    for z in zeilen(engine, text, f, r.width - 16):
        b.draw_text(z, Point(r.x + 8, y + m.ascent), f, Style(color=schrift))
        y += m.line_spacing


def verbindung(b, farbe: tuple, x_text: float, y_text: float, r: Rect, rechts: bool) -> None:
    """Linie vom Text zur Blase: waagerecht aus dem Seitenrand, dann zur Mitte der Kopfzeile."""
    x_blase = r.x if rechts else r.x + r.width
    y_blase = r.y + 12
    xm = x_blase - 10 if rechts else x_blase + 10
    stil = Style(color=farbe, width=LINIE_BREITE, cap="round", join="round")
    b.draw_path([("M", x_text, y_text), ("L", xm, y_text), ("L", x_blase, y_blase)], stil, True, False)            # ein Zug: saubere Ecke am Knick
    b.draw_ellipse(Point(x_text, y_text), ANKER_RADIUS, ANKER_RADIUS, Style(color=farbe, width=0, filled=True))      # Ankerpunkt am Ende der kommentierten Stelle
