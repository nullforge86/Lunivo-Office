"""Deckblätter (Einfügen ▸ Deckblatt): 17 Gestaltungen in den Gruppen der Vorlage (Artikel, Firma, Lebenslauf, Abschlussarbeit), je im
Hoch- oder Querformat. Keine Oberfläche.

Ein Deckblatt ist ein eigener erster Abschnitt: die Grafik liegt als ganzseitiges Bild hinter dem Text (Wasserzeichen des Abschnitts mit
``"ganzseitig": True``, siehe ``editor/seite/wasserzeichen.py``), die Platzhalter sind gewöhnliche Absätze, die man überschreibt. Das übrige
Dokument beginnt danach auf einer neuen Seite mit seiner bisherigen Einrichtung (Kopf- und Fußzeilen, Wasserzeichen, Format).
Ein neues Deckblatt ersetzt das vorhandene; ``entfernen`` nimmt es wieder heraus.

    zeichnen(p, name, rechteck, mit_text=True)    # Vorschau und Grafik, Seite in beliebigem Maßstab
    einfuegen(ed, name, quer=False)              # ed: DocumentEditor (document(), page)
    entfernen(ed) -> bool
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextFormat

from lunivo_writer.adapter.qt.geometrie import rect_from_qt
from lunivo_writer.adapter.qt.rendering import QtRenderBackend, _qfont
from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.rendering import LinearGradient, RadialGradient, RenderBackend, Style, rgba
from lunivo_writer.core.textlayout import FontSpec, TextLayoutEngine
from lunivo_writer.dienste.textsatz import standard_engine

from lunivo_writer.modelle.seite import mm_to_px

B_DECKBLATT = QTextFormat.UserProperty + 60          # an jedem Absatz des Deckblatts: Name der Gestaltung
B_DECKBLATT_UMBRUCH = QTextFormat.UserProperty + 61  # am ersten Absatz danach: sein Seitenumbruch gehört zum Deckblatt

ARTIKEL, FIRMA, LEBENSLAUF, ARBEIT = "Artikel", "Firma", "Lebenslauf", "Abschlussarbeit"


@dataclass
class Feld:
    """Ein Platzhalter-Absatz: ``y`` = Oberkante als Anteil der Blatthöhe, ``x`` = linker Rand als Anteil der Blattbreite (bei links)."""
    text: str
    pt: float
    y: float
    ausrichtung: str = "links"            # links | mitte | rechts
    fett: bool = False
    farbe: str = "#262626"
    schrift: str = "Liberation Sans"
    x: float = 0.12


@dataclass
class Gestaltung:
    name: str
    gruppe: str
    felder: list[Feld] = field(default_factory=list)


def _kontakt(y: float, farbe: str = "#262626", x: float = 0.12, ausrichtung: str = "links", abstand: float = 0.022) -> list[Feld]:
    return [Feld(t, 9, y + i * abstand, ausrichtung, False, farbe, x=x) for i, t in
            enumerate(("Name: [Ihr Name]", "Telefon: [Telefonnummer]", "E-Mail: [E-Mail-Adresse]", "Adresse: [Straße, PLZ Ort]"))]


def _arbeit(y: float, farbe: str = "#262626") -> list[Feld]:
    return [Feld(t, 10, y + i * 0.03, "mitte", False, farbe) for i, t in
            enumerate(("Name: [Ihr Name]", "Matrikelnummer: [Nummer]", "Studiengang: [Studiengang]", "Betreuer: [Name]",
                       "Abgabedatum: [Datum]"))]


SERIF = "Liberation Serif"

GESTALTUNGEN: list[Gestaltung] = [
    Gestaltung("Mosaik", ARTIKEL, [Feld("[Titel des Artikels]", 20, 0.66, fett=True), Feld("[Untertitel]", 11, 0.72),
                                   Feld("[Kurzfassung: Fassen Sie hier den Inhalt in zwei, drei Sätzen zusammen.]", 9, 0.76, farbe="#595959")]),
    Gestaltung("Himmel", ARTIKEL, [Feld("[Titel des Artikels]", 20, 0.36, "mitte", farbe="#404040", schrift=SERIF),
                                   Feld("[Kurzfassung des Inhalts]", 9, 0.42, "mitte", farbe="#595959"),
                                   Feld("[Autor]", 10, 0.80, "rechts"), Feld("[Datum]", 10, 0.83, "rechts")]),
    Gestaltung("Sonne", ARTIKEL, [Feld("[Titel des Artikels]", 20, 0.74, "mitte", True, schrift=SERIF), Feld("[Autor]", 10, 0.80, "mitte")]),
    Gestaltung("Kopfbalken", ARTIKEL, [Feld("[Firmenname]", 9, 0.07, "links", farbe="#ffffff", x=0.20),
                                       Feld("[Titel in zwei bis fünf Wörtern]", 18, 0.24, "mitte", farbe="#2f6eba"),
                                       Feld("[Kurzfassung des Inhalts]", 9, 0.30, "mitte", farbe="#595959"),
                                       Feld("[Autor]", 10, 0.42, "mitte")]),
    Gestaltung("Wellen", FIRMA, [Feld("LOGO · [Firmenname]", 10, 0.06, farbe="#7b2f8f", x=0.18),
                                 Feld("[Titel des Dokuments]", 18, 0.22, farbe="#7b2f8f", x=0.18),
                                 Feld("[Untertitel]", 10, 0.27, farbe="#a65fb8", x=0.18)]),
    Gestaltung("Blaurand", LEBENSLAUF, [Feld("LEBENSLAUF", 26, 0.20, "mitte", True, "#2f6eba", SERIF)]
               + _kontakt(0.52, x=0.30)),
    Gestaltung("Stadt", LEBENSLAUF, _kontakt(0.08, x=0.30)
               + [Feld("LEBENSLAUF", 32, 0.32, "mitte", True, "#262626", SERIF)]),
    Gestaltung("Notizzettel", LEBENSLAUF, [Feld("LEBENSLAUF", 18, 0.44, "rechts", True, "#5a4a00", SERIF)]
               + _kontakt(0.51, "#3b3200", ausrichtung="rechts")),
    Gestaltung("Sonnenblume", LEBENSLAUF, [Feld("LEBENSLAUF", 30, 0.14, "mitte", True, "#e08a00", SERIF)]
               + _kontakt(0.64, x=0.56)),
    Gestaltung("Grün", LEBENSLAUF, [Feld("LEBENSLAUF", 26, 0.14, "links", True, "#6b8e23", SERIF)] + _kontakt(0.58)),
    Gestaltung("Puzzle", LEBENSLAUF, [Feld("LEBENSLAUF", 24, 0.48, "mitte", True, "#6b8e23", SERIF)] + _kontakt(0.58, x=0.30)),
    Gestaltung("Segel", LEBENSLAUF, _kontakt(0.08, "#ffffff", x=0.18)
               + [Feld("LEBENSLAUF", 28, 0.44, "mitte", True, "#ffffff", SERIF)]),
    Gestaltung("Schlicht", ARBEIT, [Feld("[Name der Hochschule]", 11, 0.12, "mitte", True), Feld("[TITEL DER ARBEIT]", 13, 0.22, "mitte"),
                                    Feld("[Art der Arbeit]", 10, 0.27, "mitte")] + _arbeit(0.50)),
    Gestaltung("Abschlussarbeit", ARBEIT, [Feld("[Name der Hochschule]", 10, 0.10, "mitte"),
                                           Feld("ABSCHLUSSARBEIT", 22, 0.20, "mitte", True, schrift=SERIF),
                                           Feld("[TITEL DER ARBEIT]", 12, 0.27, "mitte")] + _arbeit(0.52)),
    Gestaltung("Rahmen", ARBEIT, [Feld("[Logo der Hochschule]", 9, 0.10, "mitte", farbe="#7f7f7f"),
                                  Feld("ABSCHLUSSARBEIT", 18, 0.22, "mitte", True, "#2f5597", SERIF),
                                  Feld("[TITEL DER ARBEIT]", 11, 0.28, "mitte")] + _arbeit(0.50)),
    Gestaltung("Linien", ARBEIT, [Feld("[Logo der Hochschule]", 9, 0.06, "mitte", farbe="#7f7f7f"),
                                  Feld("ABSCHLUSSARBEIT", 24, 0.14, "mitte", True, "#1f3864", SERIF),
                                  Feld("[TITEL DER ARBEIT]", 11, 0.22, "mitte")] + _arbeit(0.42)),
    Gestaltung("Siegel", ARBEIT, [Feld("[Name der Hochschule]", 12, 0.22, "mitte", True), Feld("BACHELORARBEIT", 10, 0.27, "mitte", True),
                                  Feld("[TITEL DER ARBEIT]", 10, 0.31, "mitte")] + _arbeit(0.42)),
]
NAMEN = [g.name for g in GESTALTUNGEN]
_NACH_NAME = {g.name: g for g in GESTALTUNGEN}


def gestaltung(name: str) -> Gestaltung:
    return _NACH_NAME.get(name, GESTALTUNGEN[0])


# ---- Grafik (über ``core.rendering.RenderBackend``) ------------------------------------------------------------------------------
def _stil(farbe: str, alpha: int = 255) -> Style:
    return Style(color=rgba(farbe, alpha), width=0, filled=True)


def _verlauf(r: Rect, farben, senkrecht: bool = True) -> LinearGradient:
    ende = Point(r.x, r.bottom) if senkrecht else Point(r.right, r.y)
    return LinearGradient(Point(r.x, r.y), ende, tuple((i / max(1, len(farben) - 1), rgba(f)) for i, f in enumerate(farben)))


def _flaeche(b: RenderBackend, r: Rect, fuellung) -> None:
    """Rechteck füllen: Farbe (``#rrggbb``) oder Verlauf."""
    if isinstance(fuellung, str):
        b.draw_rect(r, _stil(fuellung))
    else:
        b.draw_rect(r, Style(width=0, filled=True, fill=fuellung))


def _wolken(b: RenderBackend, r: Rect, y: float, farbe: str = "#ffffff", n: int = 5) -> None:
    stil = _stil(farbe)
    for i in range(n):
        cx = r.x + r.width * (0.1 + 0.2 * i)
        cy = r.y + r.height * (y + 0.03 * math.sin(i * 1.7))
        for dx, dy, s in ((0, 0, 0.09), (0.06, 0.01, 0.07), (-0.06, 0.015, 0.06)):
            b.draw_ellipse(Point(cx + dx * r.width, cy + dy * r.height), s * r.width, s * r.width * 0.55, stil)


def _dreieck(x1, y1, x2, y2, x3, y3) -> list:
    return [("M", x1, y1), ("L", x2, y2), ("L", x3, y3), ("Z",)]


def _segelboot(b: RenderBackend, x: float, y: float, s: float) -> None:
    stil = _stil("#f2f2f2")
    b.draw_path(_dreieck(x, y, x, y - 2.2 * s, x + 1.1 * s, y), stil)
    b.draw_path(_dreieck(x - 0.1 * s, y, x - 0.1 * s, y - 1.8 * s, x - 0.9 * s, y), stil)
    b.draw_rect(Rect(x - 1.0 * s, y, 2.3 * s, 0.18 * s), _stil("#d9d9d9"))


def _puzzle(b: RenderBackend, x: float, y: float, s: float, farbe: str) -> None:
    nase = s * 0.18
    b.draw_path([("R", x, y, s, s), ("E", x + s, y + s / 2, nase, nase), ("E", x + s / 2, y, nase, nase)],
                Style(color=rgba(farbe), outline=rgba("#ffffff"), width=max(1.0, s * 0.04), filled=True), union=True)


def _blume(b: RenderBackend, cx: float, cy: float, s: float) -> None:
    stil = _stil("#f5b400")
    for i in range(14):
        b.push_state(translate=Point(cx, cy), rotate=math.degrees(i * math.tau / 14))
        b.draw_ellipse(Point(s * 0.75, 0), s * 0.42, s * 0.14, stil)
        b.pop_state()
    b.draw_ellipse(Point(cx, cy), s * 0.48, s * 0.48, _stil("#5b3a12"))


def _g_mosaik(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    farben = ("#e8175d", "#f05a28", "#f7b500", "#ff8c00", "#d4145a", "#ff4e50", "#fc913a", "#f9d423")
    n = 9
    for i in range(n):
        for j in range(int(0.56 * h / (w / n))):                     # Mosaik bis gut zur Hälfte, darunter Platz für den Titel
            k = (i * 7 + j * 3) % len(farben)
            gr = 0.9 - 0.05 * ((i + j) % 4)
            b.draw_rect(Rect(x0 + (i + (1 - gr) / 2) * w / n, y0 + (j + (1 - gr) / 2) * w / n, gr * w / n, gr * w / n), _stil(farben[k]))
    _flaeche(b, R(0, 0.57, 1, 0.012), "#e8175d")


def _g_himmel(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    _flaeche(b, R(0, 0, 1, 0.55), _verlauf(R(0, 0, 1, 0.55), ("#9fd3f2", "#e6f4fc", "#ffffff")))
    b.push_state(opacity=0.7); _wolken(b, r, 0.12, "#ffffff", 4); b.pop_state()


def _g_sonne(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    _flaeche(b, R(0, 0, 1, 0.68), _verlauf(R(0, 0, 1, 0.68), ("#f7a600", "#fbd34d", "#fff1b8")))
    mitte = Point(x0 + 0.7 * w, y0 + 0.36 * h)
    glanz = RadialGradient(mitte, 0.3 * w, ((0, rgba("#ffffff")), (0.25, rgba("#fff6c9")), (1, (255, 246, 201, 0))))
    b.draw_ellipse(mitte, 0.3 * w, 0.3 * w, Style(width=0, filled=True, fill=glanz))
    b.push_state(opacity=0.8); _wolken(b, r, 0.16, "#ffffff", 5); b.pop_state()
    b.draw_ellipse(Point(x0 + 0.88 * w, y0 + 0.6 * h), 0.03 * w, 0.06 * h, _stil("#1a1a1a"))


def _g_kopfbalken(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    _flaeche(b, R(0.06, 0.04, 0.88, 0.14), _verlauf(R(0.06, 0.04, 0.88, 0.14), ("#2f6eba", "#8fc1ef"), False))
    _flaeche(b, R(0.06, 0.035, 0.88, 0.004), "#9dc3e6")


def _g_wellen(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    b.draw_rect(R(0.15, 0.045, 0.28, 0.04), Style(color=rgba("#7b2f8f"), width=max(1.0, w * 0.004)))
    for i in range(7):
        ops = [("M", x0, y0 + (0.55 + i * 0.06) * h)]
        for k in range(1, 9):
            ops.append(("Q", x0 + (k - 0.5) / 8 * w, y0 + (0.52 + i * 0.06 + 0.05 * ((k % 2) * 2 - 1)) * h, x0 + k / 8 * w, y0 + (0.55 + i * 0.06) * h))
        b.draw_path(ops, Style(color=(200, 200, 210, 140), width=max(1.0, w * 0.01)))


def _g_blaurand(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    for x in (0.0, 0.94):
        _flaeche(b, R(x, 0, 0.06, 1), "#2f6eba")
    _flaeche(b, R(0, 0, 1, 0.012), "#2f6eba"); _flaeche(b, R(0, 0.988, 1, 0.012), "#2f6eba")


def _g_stadt(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    hoehen = (0.10, 0.16, 0.08, 0.20, 0.13, 0.18, 0.09, 0.15, 0.22, 0.11, 0.17, 0.12)
    for i, hh in enumerate(hoehen):
        b.draw_rect(R(i / len(hoehen), 1 - hh, 1 / len(hoehen) * 0.9, hh), _stil("#e3e3e3"))
    for i, hh in enumerate(hoehen[::-1]):
        b.draw_rect(R((i + 0.4) / len(hoehen), 1 - hh * 0.6, 1 / len(hoehen) * 0.6, hh * 0.6), _stil("#f2f2f2"))


def _g_notizzettel(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    _flaeche(b, r, "#5b8fd6")
    for i in range(9):
        _puzzle(b, x0 + (0.04 + 0.025 * i + 0.01 * (i % 2)) * w, y0 + (0.05 + 0.03 * i) * h, 0.05 * w, "#f6d32d")
    b.push_state(translate=Point(x0 + 0.62 * w, y0 + 0.47 * h), rotate=-6)
    b.draw_rect(Rect(-0.25 * w + 4, -0.08 * h + 4, 0.52 * w, 0.18 * h), _stil("#000000", 50))
    b.draw_rect(Rect(-0.25 * w, -0.08 * h, 0.52 * w, 0.18 * h), _stil("#f6d32d"))
    b.pop_state()


def _g_sonnenblume(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    _flaeche(b, R(0, 0, 1, 0.7), _verlauf(R(0, 0, 1, 0.7), ("#5aa9e6", "#bfe1f7", "#ffffff")))
    b.push_state(opacity=0.9); _wolken(b, r, 0.42, "#ffffff", 5); b.pop_state()
    for cx in (0.2, 0.42):
        b.draw_line(Point(x0 + cx * w, y0 + 0.82 * h), Point(x0 + cx * w, y0 + h), Style(color=rgba("#3c7a1e"), width=max(1.0, w * 0.02)))
    _blume(b, x0 + 0.2 * w, y0 + 0.8 * h, 0.14 * w); _blume(b, x0 + 0.42 * w, y0 + 0.9 * h, 0.1 * w)


def _g_gruen(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    for i, (fx, fy, s, f) in enumerate(((0.86, 0.62, 0.22, "#c5e17a"), (0.95, 0.72, 0.18, "#9acd32"), (0.80, 0.80, 0.16, "#e2f0b8"))):
        b.push_state(translate=Point(x0 + fx * w, y0 + fy * h), rotate=30 + i * 40)
        b.draw_ellipse(Point(0, 0), s * w, s * w * 0.35, _stil(f))
        b.pop_state()


def _g_puzzle(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    ops = [("M", x0, y0 + 0.02 * h), ("Q", x0 + 0.5 * w, y0 + 0.02 * h, x0 + w, y0 + 0.24 * h), ("L", x0 + w, y0), ("L", x0, y0), ("Z",)]
    b.draw_path(ops, Style(width=0, filled=True, fill=_verlauf(R(0, 0, 1, 0.24), ("#3a8dde", "#bfe0fb"), False)))
    for i, (fx, fy, f) in enumerate(((0.62, 0.10, "#2e86de"), (0.72, 0.08, "#20bf6b"), (0.66, 0.18, "#f7b731"), (0.78, 0.17, "#2e86de"),
                                     (0.86, 0.12, "#20bf6b"), (0.02, 0.92, "#2e86de"))):
        _puzzle(b, x0 + fx * w, y0 + fy * h, 0.09 * w, f)


def _g_segel(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    _flaeche(b, r, _verlauf(r, ("#0b1f44", "#1b3f7a", "#5c86c4")))
    _flaeche(b, R(0, 0.82, 1, 0.18), _verlauf(R(0, 0.82, 1, 0.18), ("#2c5aa0", "#0b1f44")))
    _segelboot(b, x0 + 0.3 * w, y0 + 0.86 * h, 0.12 * w); _segelboot(b, x0 + 0.66 * w, y0 + 0.88 * h, 0.09 * w)
    b.draw_line(Point(x0 + 0.18 * w, y0 + 0.43 * h), Point(x0 + 0.82 * w, y0 + 0.43 * h), Style(color=rgba("#ffffff"), width=max(1.0, w * 0.003)))


def _g_rahmen(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    b.draw_rect(R(0.07, 0.05, 0.86, 0.9), Style(color=rgba("#2f5597"), width=max(1.0, w * 0.004)))
    b.draw_rect(R(0.38, 0.08, 0.24, 0.04), Style(color=rgba("#9dc3e6"), width=max(1.0, w * 0.002)))


def _g_linien(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    _flaeche(b, R(0, 0, 1, 0.012), "#2f5597"); _flaeche(b, R(0, 0.985, 1, 0.015), "#2f5597")
    b.draw_rect(R(0.38, 0.045, 0.24, 0.035), Style(color=rgba("#9dc3e6"), width=max(1.0, w * 0.002)))


def _g_siegel(b: RenderBackend, r: Rect, w: float, h: float, x0: float, y0: float, R) -> None:
    stil = Style(color=rgba("#404040"), width=max(1.0, w * 0.006))
    b.draw_ellipse(Point(x0 + 0.2 * w, y0 + 0.1 * h), 0.06 * w, 0.06 * w, stil)
    b.draw_ellipse(Point(x0 + 0.2 * w, y0 + 0.1 * h), 0.035 * w, 0.035 * w, stil)


_GRAFIKEN = {
    "Mosaik": _g_mosaik,
    "Himmel": _g_himmel,
    "Sonne": _g_sonne,
    "Kopfbalken": _g_kopfbalken,
    "Wellen": _g_wellen,
    "Blaurand": _g_blaurand,
    "Stadt": _g_stadt,
    "Notizzettel": _g_notizzettel,
    "Sonnenblume": _g_sonnenblume,
    "Grün": _g_gruen,
    "Puzzle": _g_puzzle,
    "Segel": _g_segel,
    "Rahmen": _g_rahmen,
    "Linien": _g_linien,
    "Siegel": _g_siegel,
}


def _grafik(b: RenderBackend, name: str, r: Rect) -> None:
    """Die Grafik einer Gestaltung (ohne Text) auf das Blatt ``r``."""
    w, h, x0, y0 = r.width, r.height, r.x, r.y

    def R(x, y, bb, hh) -> Rect:
        return Rect(x0 + x * w, y0 + y * h, bb * w, hh * h)
    b.push_state(clip=r, antialias=True)
    zeichne = _GRAFIKEN.get(name)
    if zeichne:
        zeichne(b, r, w, h, x0, y0, R)
    b.pop_state()


def _schrift(f: Feld, blatt_hoehe_px: float, quer: bool) -> FontSpec:
    """Schrift eines Feldes im Maßstab des Blattes (Original: A4 hoch = 1123 Bildpunkte; quer etwas kleiner)."""
    px = max(1, round(f.pt * 96 / 72 * blatt_hoehe_px / 1123 * (0.85 if quer else 1.0)))
    return FontSpec(f.schrift, px * 72 / 96, 700 if f.fett else 400)


def zeichnen_mit(b: RenderBackend, name: str, r: Rect, mit_text: bool = True, engine: TextLayoutEngine | None = None) -> None:
    """Gestaltung ``name`` auf das Blatt ``r`` (weißer Grund, Grafik, auf Wunsch die Platzhalter) über ein beliebiges Rendering-Backend."""
    g = gestaltung(name)
    quer = r.width > r.height
    b.push_state()
    b.draw_rect(r, _stil("#ffffff"))
    _grafik(b, name, r)
    if mit_text:
        engine = engine or standard_engine()
        for f in g.felder:
            s = _schrift(f, r.height if not quer else r.width, quer)
            m = engine.font_metrics(s)
            x = r.x + (f.x if f.ausrichtung == "links" else 0.1) * r.width
            breite = r.right - 0.1 * r.width - x
            ausr = {"links": "left", "mitte": "center", "rechts": "right"}[f.ausrichtung]
            b.draw_text_box(f.text, Rect(x, r.y + f.y * r.height, breite, (m.ascent + m.descent) * 3), s, Style(color=rgba(f.farbe)), align=ausr, valign="top")
    b.pop_state()


def zeichnen(p, name: str, r, mit_text: bool = True) -> None:
    """Gestaltung ``name`` auf das Blatt ``r`` (QPainter, QRectF): für die Galerie."""
    zeichnen_mit(QtRenderBackend(p), name, rect_from_qt(r), mit_text)


def grafik_bild(name: str, breite_px: int, hoehe_px: int) -> QImage:
    img = QImage(breite_px, hoehe_px, QImage.Format_ARGB32)
    img.fill(QColor("#ffffff"))
    p = QPainter(img)
    _grafik(QtRenderBackend(p), name, Rect(0, 0, breite_px, hoehe_px))
    p.end()
    return img


# ---- Einfügen und Entfernen ------------------------------------------------------------------------------------------------------
def hat_deckblatt(doc) -> bool:
    return doc.firstBlock().blockFormat().hasProperty(B_DECKBLATT)


def entfernen(ed) -> bool:
    """Das Deckblatt (erster Abschnitt mit ``B_DECKBLATT``) herausnehmen; das Dokument bekommt die Einrichtung des zweiten Abschnitts."""
    from lunivo_writer.editor.seite import abschnitte as AB
    doc = ed.document()
    if not hat_deckblatt(doc) or AB.anzahl(doc) < 2:
        return False
    rest = AB.einrichtung(doc, ed.page, 1)
    if (rest.watermark or {}).get("deckblatt_leer"):
        rest.watermark = None
    elif rest.watermark:
        rest.watermark = {k: v for k, v in rest.watermark.items() if k != "abschnitt"}
    c = QTextCursor(doc)
    c.beginEditBlock()
    ziel_bf = doc.findBlock(AB.beginn(doc, 1)).blockFormat()
    eigener_umbruch = ziel_bf.property(AB.B_ABSCHNITT) if ziel_bf.hasProperty(AB.B_ABSCHNITT) else None
    c.setPosition(0); c.setPosition(AB.beginn(doc, 1), QTextCursor.KeepAnchor); c.removeSelectedText()
    AB._setze(c, eigener_umbruch)                       # Qt behält das Format des ersten Blocks: dessen Deckblatt-Umbruch darf nicht am Text bleiben
    bf = c.blockFormat()
    if bf.hasProperty(B_DECKBLATT_UMBRUCH):
        bf.clearProperty(B_DECKBLATT_UMBRUCH); bf.setPageBreakPolicy(QTextFormat.PageBreak_Auto); c.setBlockFormat(bf)
    c.endEditBlock()
    ed.page = rest
    doc.setModified(True)
    return True


def einfuegen(ed, name: str, quer: bool = False) -> None:
    """Deckblatt ``name`` als ersten Abschnitt an den Anfang setzen (ersetzt ein vorhandenes)."""
    from lunivo_writer.editor.seite import abschnitte as AB
    entfernen(ed)
    doc = ed.document()
    g = gestaltung(name)
    alt = copy.deepcopy(ed.page)
    rest = copy.deepcopy(alt)                           # das Dokument nach dem Deckblatt: alles wie bisher, Wasserzeichen nur dort
    rest.watermark = {**(alt.watermark or {}), "abschnitt": True} if alt.watermark else {"abschnitt": True, "deckblatt_leer": True}
    deck = copy.deepcopy(alt)
    deck.set_orientation(quer)
    for hf in ("header", "footer", "first_header", "first_footer", "even_header", "even_footer"):
        getattr(deck, hf).text = ""
    deck.diff_first = False
    bw, bh = mm_to_px(deck.width_mm), mm_to_px(deck.height_mm)
    deck.watermark = {"bild": _bild_text(grafik_bild(name, round(bw), round(bh))), "bild_name": f"Deckblatt {name}", "ganzseitig": True,
                      "auswaschen": False, "transparenz": 0, "winkel": 0, "abschnitt": True}
    c = QTextCursor(doc)
    c.beginEditBlock()
    c.setPosition(0)
    c.insertBlock(); c.movePosition(QTextCursor.PreviousBlock)        # neuer erster Absatz; der bisherige rückt nach unten
    oben_px = mm_to_px(deck.margin_top_mm)
    links_px, rechts_px = mm_to_px(deck.margin_left_mm), mm_to_px(deck.margin_right_mm)
    y = oben_px
    luecke = g.felder[0].y * bh - oben_px
    if luecke > 2:                                      # Qt lässt den oberen Abstand eines Absatzes oben auf der Seite weg: ein Abstandshalter
        bf = QTextBlockFormat(); bf.setLineHeight(luecke, QTextBlockFormat.LineHeightTypes.FixedHeight.value); bf.setProperty(B_DECKBLATT, name)
        cf = QTextCharFormat(); cf.setFontPointSize(1)
        c.setBlockFormat(bf); c.setBlockCharFormat(cf)
        c.insertText(" ", cf)                           # ein leerer erster Absatz verlöre beim Kopieren (Druck, PDF) seine Höhe
        y += luecke
    for i, f in enumerate(g.felder):
        s = _schrift(f, bh if not quer else bw, quer)
        ziel = f.y * bh
        bf = QTextBlockFormat()
        bf.setTopMargin(max(0.0, ziel - y))
        bf.setAlignment({"links": Qt.AlignLeft, "mitte": Qt.AlignHCenter, "rechts": Qt.AlignRight}[f.ausrichtung])
        if f.ausrichtung == "links":
            bf.setLeftMargin(max(0.0, f.x * bw - links_px))
        else:
            bf.setLeftMargin(max(0.0, 0.1 * bw - links_px)); bf.setRightMargin(max(0.0, 0.1 * bw - rechts_px))
        bf.setProperty(B_DECKBLATT, name)
        cf = QTextCharFormat(); cf.setFont(_qfont(s)); cf.setForeground(QColor(f.farbe))
        cf.setFontPointSize(f.pt * (0.85 if quer else 1.0))
        if i or luecke > 2:
            c.insertBlock(bf, cf)
        else:
            c.setBlockFormat(bf); c.setBlockCharFormat(cf)
        c.insertText(f.text, cf)
        m = standard_engine().font_metrics(s)
        y = max(y, ziel) + (m.ascent + m.descent) * 1.15
    bf = c.blockFormat(); bf.setProperty(AB.B_ABSCHNITT, AB.eintrag("naechste", rest)); c.setBlockFormat(bf)   # Deckblatt endet hier
    c.movePosition(QTextCursor.NextBlock)               # das Dokument beginnt auch in der Bearbeitungsansicht auf einem neuen Blatt
    bf = c.blockFormat()
    if not bf.pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore:
        bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore); bf.setProperty(B_DECKBLATT_UMBRUCH, True); c.setBlockFormat(bf)
    c.endEditBlock()
    ed.page = deck
    doc.setModified(True)


def _bild_text(img: QImage) -> str:
    from lunivo_writer.editor.seite.wasserzeichen import bild_zu_text
    return bild_zu_text(img)
