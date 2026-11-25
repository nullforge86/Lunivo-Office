from __future__ import annotations
from PySide6.QtWidgets import QWidget
from vcl.qt.widgets.bausteine.abstaende.raster_hilfen import Anordnung
from vcl.qt.widgets.bausteine.abstaende.raster_linie import RasterLinie


class RasterSpalte(RasterLinie):
    """Elemente untereinander."""

    def __init__(self, eltern: QWidget | None = None):
        super().__init__(True, eltern)


class RasterZeile(RasterLinie):
    """Elemente nebeneinander."""

    def __init__(self, eltern: QWidget | None = None):
        super().__init__(False, eltern)


def kanten_anordnung(plaetze: list, breite: int, hoehe: int) -> Anordnung:
    """Gitter aus Rechtecken (Element, x, y, b, h): jede Kante eines Elements wird eine Gitterlinie, jedes Element belegt die Zellen zwischen
    seinen Kanten. Spalten und Zeilen bekommen genau die Breite/Höhe zwischen zwei Linien (Abstand 0); die letzte Zeile nimmt überzählige Höhe."""
    xs = sorted({0, max(1, breite)} | {x for _it, x, _y, _b, _h in plaetze} | {x + b for _it, x, _y, b, _h in plaetze})
    ys = sorted({0, max(0, hoehe)} | {y for _it, _x, y, _b, _h in plaetze} | {y + h for _it, _x, y, _b, h in plaetze})
    xi, yi = {x: k for k, x in enumerate(xs)}, {y: k for k, y in enumerate(ys)}
    a = Anordnung(hoehe=hoehe)
    for it, x, y, b, h in plaetze:
        c0, r0 = xi[x], yi[y]
        a.zellen.append((it, r0, c0, max(1, yi[y + h] - r0), max(1, xi[x + b] - c0), None))
    a.spalten = {k: xs[k + 1] - xs[k] for k in range(len(xs) - 1)}
    a.zeilen = {k: ys[k + 1] - ys[k] for k in range(len(ys) - 1)}
    return a
