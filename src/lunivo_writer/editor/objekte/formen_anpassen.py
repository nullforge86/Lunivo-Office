"""Anpassungsgriffe der Formen (die gelbe Raute): welche Form welche Parameter hat, wie der Pfad daraus entsteht und wo der Griff liegt.

Die Parameter einer Form stehen als Liste ``adj`` (Zahlen, Anteile von Breite/Höhe) in ``daten["adj"]``; fehlt sie, gelten die Standardwerte
(= die Form ohne Anpassung, wie sie ``formen_katalog`` zeichnet). Jede anpassbare Form hat einen Eintrag in ``ANPASS``:
``standard`` (Liste), ``grenzen`` (Liste von (kleinster, größter Wert)), ``pfad(r, adj)``, ``griffe(r, adj)`` (eine Lage je Parameter) und
``wert(r, i, punkt)`` (Parameter ``i`` aus der Lage des gezogenen Griffs). Keine Oberfläche."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainterPath, QPolygonF


def _poly_pfad(punkte: list[tuple[float, float]], r: QRectF) -> QPainterPath:
    p = QPainterPath()
    p.addPolygon(QPolygonF([QPointF(r.left() + x * r.width(), r.top() + y * r.height()) for x, y in punkte]))
    p.closeSubpath()
    return p


def _pt(r: QRectF, x: float, y: float) -> QPointF:
    return QPointF(r.left() + x * r.width(), r.top() + y * r.height())


def _anteil(r: QRectF, p: QPointF) -> tuple[float, float]:
    return (p.x() - r.left()) / max(1e-9, r.width()), (p.y() - r.top()) / max(1e-9, r.height())


# ---- Rundrechtecke: [Radius] als Anteil der kürzeren Seite (0 … 0.5) --------------------------------------------------------------
def _rund(standard: float) -> dict:
    def pfad(r, a):
        p = QPainterPath(); rr = min(r.width(), r.height()) * a[0]; p.addRoundedRect(r, rr, rr)
        return p
    return {"standard": [standard], "grenzen": [(0.0, 0.5)], "pfad": pfad,
            "griffe": lambda r, a: [QPointF(r.left() + min(r.width(), r.height()) * a[0], r.top())],
            "wert": lambda r, i, p: (p.x() - r.left()) / max(1e-9, min(r.width(), r.height()))}


# ---- Sterne: [Spitzentiefe] = Innenradius als Anteil des Außenradius -------------------------------------------------------------
def _stern(zacken: int, innen: float) -> dict:
    def pfad(r, a):
        pkt = []
        for i in range(zacken * 2):
            rad = 0.5 if i % 2 == 0 else 0.5 * a[0]
            w = math.radians(-90 + i * 180 / zacken)
            pkt.append((0.5 + rad * math.cos(w), 0.5 + rad * math.sin(w)))
        return _poly_pfad(pkt, r)
    return {"standard": [innen], "grenzen": [(0.05, 0.95)], "pfad": pfad,
            "griffe": lambda r, a: [_pt(r, 0.5, 0.5 - 0.5 * a[0])],
            "wert": lambda r, i, p: (0.5 - _anteil(r, p)[1]) / 0.5}


# ---- Blockpfeile: Längsachse u (0 → 1 in Pfeilrichtung), Querachse v ---------------------------------------------------------------
_RICHTUNG = {"rechts": lambda u, v: (u, v), "links": lambda u, v: (1 - u, v), "unten": lambda u, v: (v, u), "oben": lambda u, v: (v, 1 - u)}
_RUECK = {"rechts": lambda x, y: (x, y), "links": lambda x, y: (1 - x, y), "unten": lambda x, y: (y, x), "oben": lambda x, y: (1 - y, x)}


def _pfeil(richtung: str, schaft: float, kopf: float) -> dict:
    """[Schaft (Dicke als Anteil der Quermaße), Kopf (Länge des Kopfes als Anteil der Längsmaße)]."""
    f, rf = _RICHTUNG[richtung], _RUECK[richtung]

    def pfad(r, a):
        s, k = a
        u0 = 1 - k
        return _poly_pfad([f(0, 0.5 - s / 2), f(u0, 0.5 - s / 2), f(u0, 0), f(1, 0.5), f(u0, 1), f(u0, 0.5 + s / 2), f(0, 0.5 + s / 2)], r)

    def griffe(r, a):
        return [_pt(r, *f(0.5 * (1 - a[1]), 0.5 - a[0] / 2)), _pt(r, *f(1 - a[1], 0))]

    def wert(r, i, p):
        x, y = _anteil(r, p)
        u, v = rf(x, y)
        return (1 - 2 * v) if i == 0 else 1 - u
    return {"standard": [schaft, kopf], "grenzen": [(0.05, 1.0), (0.05, 0.95)], "pfad": pfad, "griffe": griffe, "wert": wert}


def _doppelpfeil(waagrecht: bool, schaft: float, kopf: float) -> dict:
    """[Schaft, Kopf (je Seite, Anteil der Längsmaße 0 … 0.5)]."""
    def f(u, v):
        return (u, v) if waagrecht else (v, u)

    def pfad(r, a):
        s, k = a
        return _poly_pfad([f(0, 0.5), f(k, 0), f(k, 0.5 - s / 2), f(1 - k, 0.5 - s / 2), f(1 - k, 0), f(1, 0.5), f(1 - k, 1),
                           f(1 - k, 0.5 + s / 2), f(k, 0.5 + s / 2), f(k, 1)], r)

    def griffe(r, a):
        return [_pt(r, *f(0.5, 0.5 - a[0] / 2)), _pt(r, *f(a[1], 0))]

    def wert(r, i, p):
        x, y = _anteil(r, p)
        u, v = (x, y) if waagrecht else (y, x)
        return (1 - 2 * v) if i == 0 else u
    return {"standard": [schaft, kopf], "grenzen": [(0.05, 1.0), (0.05, 0.5)], "pfad": pfad, "griffe": griffe, "wert": wert}


def _fuenfeckpfeil(kopf: float) -> dict:
    return {"standard": [kopf], "grenzen": [(0.05, 0.95)],
            "pfad": lambda r, a: _poly_pfad([(0, 0), (1 - a[0], 0), (1, 0.5), (1 - a[0], 1), (0, 1)], r),
            "griffe": lambda r, a: [_pt(r, 1 - a[0], 0)], "wert": lambda r, i, p: 1 - _anteil(r, p)[0]}


# ---- Weitere Formen --------------------------------------------------------------------------------------------------------------
def _kreuz(arm: float) -> dict:
    """[Armdicke] als Anteil von Breite und Höhe."""
    def pfad(r, a):
        o, u = 0.5 - a[0] / 2, 0.5 + a[0] / 2
        return _poly_pfad([(o, 0), (u, 0), (u, o), (1, o), (1, u), (u, u), (u, 1), (o, 1), (o, u), (0, u), (0, o), (o, o)], r)
    return {"standard": [arm], "grenzen": [(0.05, 1.0)], "pfad": pfad,
            "griffe": lambda r, a: [_pt(r, 0.5 - a[0] / 2, 0)], "wert": lambda r, i, p: 1 - 2 * _anteil(r, p)[0]}


def _trapez(neigung: float) -> dict:
    """[Neigung] = Versatz der kurzen Seite als Anteil der Breite (0 … 0.5)."""
    return {"standard": [neigung], "grenzen": [(0.0, 0.5)],
            "pfad": lambda r, a: _poly_pfad([(a[0], 0), (1 - a[0], 0), (1, 1), (0, 1)], r),
            "griffe": lambda r, a: [_pt(r, a[0], 0)], "wert": lambda r, i, p: _anteil(r, p)[0]}


def _parallelogramm(neigung: float) -> dict:
    return {"standard": [neigung], "grenzen": [(0.0, 0.9)],
            "pfad": lambda r, a: _poly_pfad([(a[0], 0), (1, 0), (1 - a[0], 1), (0, 1)], r),
            "griffe": lambda r, a: [_pt(r, a[0], 0)], "wert": lambda r, i, p: _anteil(r, p)[0]}


def _dreieck(spitze: float) -> dict:
    """[Lage der Spitze] als Anteil der Breite (0 … 1)."""
    return {"standard": [spitze], "grenzen": [(0.0, 1.0)],
            "pfad": lambda r, a: _poly_pfad([(a[0], 0), (1, 1), (0, 1)], r),
            "griffe": lambda r, a: [_pt(r, a[0], 0)], "wert": lambda r, i, p: _anteil(r, p)[0]}


def _ring(dicke: float) -> dict:
    """[Dicke] des Rings als Anteil der kürzeren Seite (0.05 … 0.5)."""
    def pfad(r, a):
        p = QPainterPath(); p.addEllipse(r)
        d = min(r.width(), r.height()) * a[0]
        innen = QPainterPath(); innen.addEllipse(r.adjusted(d, d, -d, -d))
        return p.subtracted(innen)
    return {"standard": [dicke], "grenzen": [(0.05, 0.5)], "pfad": pfad,
            "griffe": lambda r, a: [QPointF(r.center().x(), r.top() + min(r.width(), r.height()) * a[0])],
            "wert": lambda r, i, p: (p.y() - r.top()) / max(1e-9, min(r.width(), r.height()))}


ANPASS: dict[str, dict] = {
    "Abgerundetes Rechteck": _rund(0.18), "Alternativer Prozess": _rund(0.25), "Grenzstelle": _rund(0.5),
    "Stern mit 4 Zacken": _stern(4, 0.38), "Stern mit 5 Zacken": _stern(5, 0.42), "Stern mit 6 Zacken": _stern(6, 0.55),
    "Stern mit 8 Zacken": _stern(8, 0.6), "Stern mit 10 Zacken": _stern(10, 0.68), "Stern mit 12 Zacken": _stern(12, 0.72),
    "Stern mit 16 Zacken": _stern(16, 0.78), "Stern mit 24 Zacken": _stern(24, 0.82), "Stern mit 32 Zacken": _stern(32, 0.85),
    "Pfeil nach rechts": _pfeil("rechts", 0.5, 0.4), "Pfeil nach links": _pfeil("links", 0.5, 0.4),
    "Pfeil nach oben": _pfeil("oben", 0.5, 0.4), "Pfeil nach unten": _pfeil("unten", 0.5, 0.4),
    "Pfeil links und rechts": _doppelpfeil(True, 0.5, 0.25), "Pfeil oben und unten": _doppelpfeil(False, 0.5, 0.25),
    "Fünfeck-Pfeil": _fuenfeckpfeil(0.3), "Kreuz": _kreuz(0.34), "Trapez": _trapez(0.22), "Parallelogramm": _parallelogramm(0.25),
    "Dreieck": _dreieck(0.5), "Ring": _ring(0.25),
}


def anpassbar(name: str) -> bool:
    return name in ANPASS


def standard(name: str) -> list[float]:
    return list(ANPASS[name]["standard"]) if name in ANPASS else []


def _voll(name: str, adj) -> list[float]:
    """Die Parameter mit Standardwerten für fehlende Stellen, auf die Grenzen begrenzt."""
    e = ANPASS[name]
    adj = list(adj or [])
    return [min(max(float(adj[i]) if i < len(adj) else e["standard"][i], lo), hi) for i, (lo, hi) in enumerate(e["grenzen"])]


def pfad(name: str, r: QRectF, adj=None) -> QPainterPath:
    return ANPASS[name]["pfad"](r, _voll(name, adj))


def griffe(name: str, r: QRectF, adj=None) -> list[QPointF]:
    """Die Lage der Anpassungsgriffe (je Parameter einer) im selben Koordinatensystem wie ``r``."""
    return ANPASS[name]["griffe"](r, _voll(name, adj)) if name in ANPASS else []


def setzen(name: str, wert: float, adj=None, index: int = 0) -> list[float]:
    """Neue Parameterliste: Parameter ``index`` = ``wert`` (auf die Grenzen begrenzt), die anderen bleiben."""
    if name not in ANPASS:
        return []
    a = _voll(name, adj)
    if 0 <= index < len(a):
        lo, hi = ANPASS[name]["grenzen"][index]
        a[index] = min(max(float(wert), lo), hi)
    return a


def wert_aus_punkt(name: str, r: QRectF, punkt: QPointF, index: int = 0) -> float:
    """Der Parameter ``index``, wenn der Griff an ``punkt`` gezogen wird (auf die Grenzen begrenzt)."""
    if name not in ANPASS or not 0 <= index < len(ANPASS[name]["grenzen"]):
        return 0.0
    lo, hi = ANPASS[name]["grenzen"][index]
    return min(max(ANPASS[name]["wert"](r, index, punkt), lo), hi)
