"""Füllung und Rahmen einer Tabellenzelle (und eines Rahmens im Text) als Zeichenanweisungen, ohne Qt: aus den Eigenschaften des Zellformats und des Tabellenformats (Namen wie im Modell, siehe ``core/document``)
entstehen ``("rect", Rect, Style)`` und ``("line", Point, Point, Style)``; ``ausfuehren`` gibt sie an ein ``RenderTarget``. Die Rechnung hängt nicht vom Backend ab."""
from __future__ import annotations

from lunivo_writer.core.document.values import Brush
from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.rendering.backend import RenderTarget, Style

RAND_KEIN, RAND_PUNKTE, RAND_STRICHE = 0, 1, 2                       # Werte von QTextFrameFormat.BorderStyle
STANDARD_RANDSTIL = 10                                                # Qt-Standard der Tabelle (Outset): wird als durchgezogene Linie gezeichnet
KANTEN = ("Top", "Left", "Bottom", "Right")
Anweisung = tuple


def _farbe(b) -> tuple[int, int, int, int] | None:
    if not isinstance(b, Brush) or b.style == 0:
        return None
    c = b.color
    return c.r, c.g, c.b, c.a


def _kante(name: str, r: Rect) -> tuple[Point, Point]:
    return {"Top": (Point(r.x, r.y), Point(r.right, r.y)), "Left": (Point(r.x, r.y), Point(r.x, r.bottom)),
            "Bottom": (Point(r.x, r.bottom), Point(r.right, r.bottom)), "Right": (Point(r.right, r.y), Point(r.right, r.bottom))}[name]


def zelle_anweisungen(rect: Rect, zelle: dict, tabelle: dict, rand: float, zoom: float) -> list[Anweisung]:
    """``rect``: die Zelle auf dem Blatt; ``rand``: Rahmenstärke der Tabelle (mit Zoom); ``zelle``/``tabelle``: Eigenschaften der Formate."""
    aus: list[Anweisung] = []
    fuell = _farbe(zelle.get("BackgroundBrush"))
    if fuell is not None:
        aus.append(("rect", rect, Style(color=fuell, width=0, filled=True)))
    for name in KANTEN:
        eigen = f"TableCell{name}Border" in zelle
        breite = float(zelle[f"TableCell{name}Border"]) * zoom if eigen else rand
        stil = int(zelle.get(f"TableCell{name}BorderStyle", STANDARD_RANDSTIL)) if eigen else int(tabelle.get("FrameBorderStyle", STANDARD_RANDSTIL))
        if breite <= 0 or stil == RAND_KEIN:
            continue
        farbe = _farbe(zelle.get(f"TableCell{name}BorderBrush") if eigen else tabelle.get("FrameBorderBrush")) or (0, 0, 0, 255)
        a, b = _kante(name, rect)
        aus.append(("line", a, b, Style(color=farbe, width=max(1.0, breite), dash={RAND_PUNKTE: "dot", RAND_STRICHE: "dash"}.get(stil))))
    return aus


def rahmen_anweisungen(rect: Rect, rahmen: dict) -> list[Anweisung]:
    """Füllung und Rahmenstrich eines Rahmens im Text (``rahmen``: Eigenschaften des Rahmenformats)."""
    aus: list[Anweisung] = []
    fuell = _farbe(rahmen.get("BackgroundBrush"))
    if fuell is not None:
        aus.append(("rect", rect, Style(color=fuell, width=0, filled=True)))
    breite = float(rahmen.get("FrameBorder", 0.0) or 0.0)
    stil = int(rahmen.get("FrameBorderStyle", STANDARD_RANDSTIL))
    if breite > 0 and stil != RAND_KEIN:
        farbe = _farbe(rahmen.get("FrameBorderBrush")) or (0, 0, 0, 255)
        for name in KANTEN:
            a, b = _kante(name, rect)
            aus.append(("line", a, b, Style(color=farbe, width=max(1.0, breite), dash={RAND_PUNKTE: "dot", RAND_STRICHE: "dash"}.get(stil))))
    return aus


def ausfuehren(backend: RenderTarget, anweisungen: list[Anweisung]) -> None:
    for a in anweisungen:
        if a[0] == "rect":
            backend.draw_rect(a[1], a[2])
        else:
            backend.draw_line(a[1], a[2], a[3])
