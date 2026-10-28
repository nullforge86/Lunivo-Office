"""Die Formen der Galerie Einfügen ▸ Formen, nach Gruppen wie in der Vorlage: Linie, Rechteck, Standardformen, Blockpfeile, Formelformen,
Flussdiagramm, Sterne und Banner, Legenden. Jede Form ist ein ``QPainterPath`` im Rechteck ``r``; keine Oberfläche.

    pfad("Fünfeck", QRectF(0, 0, 100, 80))    # → QPainterPath
    ist_linie("Pfeil")                         # True: nur Strich, keine Füllung
"""
from __future__ import annotations

import math
from typing import Callable

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainterPath, QPolygonF

Pfad = Callable[[QRectF], QPainterPath]


def _poly(*punkte: tuple[float, float]) -> Pfad:
    """Vieleck aus Anteilen (0…1) der Breite und Höhe."""
    def f(r: QRectF) -> QPainterPath:
        p = QPainterPath()
        p.addPolygon(QPolygonF([QPointF(r.left() + x * r.width(), r.top() + y * r.height()) for x, y in punkte]))
        p.closeSubpath()
        return p
    return f


def _vieleck(n: int, drehung: float = -90) -> Pfad:
    return _poly(*[(0.5 + 0.5 * math.cos(math.radians(drehung + i * 360 / n)), 0.5 + 0.5 * math.sin(math.radians(drehung + i * 360 / n)))
                   for i in range(n)])


def _stern(zacken: int, innen: float = 0.42) -> Pfad:
    pkt = []
    for i in range(zacken * 2):
        rad = 0.5 if i % 2 == 0 else 0.5 * innen
        w = math.radians(-90 + i * 180 / zacken)
        pkt.append((0.5 + rad * math.cos(w), 0.5 + rad * math.sin(w)))
    return _poly(*pkt)


def _linie(*punkte: tuple[float, float], pfeil_ende: bool = False, pfeil_anfang: bool = False) -> Pfad:
    def f(r: QRectF) -> QPainterPath:
        pts = [QPointF(r.left() + x * r.width(), r.top() + y * r.height()) for x, y in punkte]
        p = QPainterPath(pts[0])
        for q in pts[1:]:
            p.lineTo(q)
        for spitze, davor in ((pts[-1], pts[-2]) if pfeil_ende else (None, None), (pts[0], pts[1]) if pfeil_anfang else (None, None)):
            if spitze is None:
                continue
            w = math.atan2(spitze.y() - davor.y(), spitze.x() - davor.x())
            lg = min(r.width(), r.height()) * 0.18 + 4
            for d in (2.6, -2.6):
                p.moveTo(spitze); p.lineTo(spitze.x() + lg * math.cos(w + d), spitze.y() + lg * math.sin(w + d))
        return p
    return f


def _bogen(start: float, spanne: float) -> Pfad:
    def f(r: QRectF) -> QPainterPath:
        p = QPainterPath(); p.arcMoveTo(r, start); p.arcTo(r, start, spanne)
        return p
    return f


def _abgerundet(radius: float = 0.18) -> Pfad:
    def f(r: QRectF) -> QPainterPath:
        p = QPainterPath(); rr = min(r.width(), r.height()) * radius; p.addRoundedRect(r, rr, rr)
        return p
    return f


def _ellipse(r: QRectF) -> QPainterPath:
    p = QPainterPath(); p.addEllipse(r)
    return p


def _ring(r: QRectF) -> QPainterPath:
    p = _ellipse(r); innen = QPainterPath(); d = min(r.width(), r.height()) * 0.25
    innen.addEllipse(r.adjusted(d, d, -d, -d))
    return p.subtracted(innen)


def _zylinder(r: QRectF) -> QPainterPath:
    h = r.height() * 0.18
    p = QPainterPath(); p.moveTo(r.left(), r.top() + h / 2)
    p.arcTo(QRectF(r.left(), r.top(), r.width(), h), 180, -180)
    p.lineTo(r.right(), r.bottom() - h / 2)
    p.arcTo(QRectF(r.left(), r.bottom() - h, r.width(), h), 0, -180)
    p.closeSubpath()
    p.moveTo(r.left(), r.top() + h / 2); p.arcTo(QRectF(r.left(), r.top(), r.width(), h), 180, 180)
    return p


def _herz(r: QRectF) -> QPainterPath:
    p = QPainterPath(); x, y, b, h = r.left(), r.top(), r.width(), r.height()
    p.moveTo(x + b / 2, y + h)
    p.cubicTo(x - b * 0.1, y + h * 0.55, x + b * 0.05, y - h * 0.1, x + b / 2, y + h * 0.25)
    p.cubicTo(x + b * 0.95, y - h * 0.1, x + b * 1.1, y + h * 0.55, x + b / 2, y + h)
    return p


def _mond(r: QRectF) -> QPainterPath:
    aussen = _ellipse(r); innen = QPainterPath(); innen.addEllipse(r.translated(r.width() * 0.3, 0))
    return aussen.subtracted(innen)


def _smiley(r: QRectF) -> QPainterPath:
    p = _ellipse(r); w, h = r.width(), r.height()
    for x in (0.33, 0.67):
        p.addEllipse(QRectF(r.left() + w * x - w * 0.05, r.top() + h * 0.3, w * 0.1, h * 0.12))
    p.moveTo(r.left() + w * 0.28, r.top() + h * 0.62); p.quadTo(r.left() + w * 0.5, r.top() + h * 0.85, r.left() + w * 0.72, r.top() + h * 0.62)
    return p


def _wolke(r: QRectF) -> QPainterPath:
    p = QPainterPath(); p.setFillRule(Qt.WindingFill)
    for x, y, d in ((0.1, 0.35, 0.4), (0.3, 0.15, 0.45), (0.55, 0.12, 0.4), (0.62, 0.35, 0.38), (0.35, 0.45, 0.45), (0.05, 0.5, 0.35)):
        p.addEllipse(QRectF(r.left() + x * r.width(), r.top() + y * r.height(), d * r.width(), d * r.height()))
    return p.simplified()


def _dokument(r: QRectF) -> QPainterPath:
    p = QPainterPath(); x, y, b, h = r.left(), r.top(), r.width(), r.height()
    p.moveTo(x, y); p.lineTo(x + b, y); p.lineTo(x + b, y + h * 0.82)
    p.cubicTo(x + b * 0.75, y + h * 0.7, x + b * 0.5, y + h * 1.05, x, y + h * 0.88); p.closeSubpath()
    return p


def _welle(r: QRectF) -> QPainterPath:
    p = QPainterPath(); x, y, b, h = r.left(), r.top(), r.width(), r.height()
    p.moveTo(x, y + h * 0.15); p.cubicTo(x + b * 0.35, y - h * 0.1, x + b * 0.65, y + h * 0.4, x + b, y + h * 0.15)
    p.lineTo(x + b, y + h * 0.85); p.cubicTo(x + b * 0.65, y + h * 1.1, x + b * 0.35, y + h * 0.6, x, y + h * 0.85); p.closeSubpath()
    return p


def _legende(form: Pfad) -> Pfad:
    def f(r: QRectF) -> QPainterPath:
        koerper = QRectF(r.left(), r.top(), r.width(), r.height() * 0.75)
        p = form(koerper)
        spitze = QPainterPath(); spitze.addPolygon(QPolygonF([QPointF(r.left() + r.width() * 0.22, koerper.bottom() - 2),
                                                              QPointF(r.left() + r.width() * 0.12, r.bottom()),
                                                              QPointF(r.left() + r.width() * 0.4, koerper.bottom() - 2)]))
        return p.united(spitze)
    return f


def _rechteck(r: QRectF) -> QPainterPath:
    p = QPainterPath(); p.addRect(r)
    return p


_LINIEN = {"Linie": _linie((0, 0.5), (1, 0.5)), "Pfeil": _linie((0, 0.5), (1, 0.5), pfeil_ende=True),
           "Doppelpfeil": _linie((0, 0.5), (1, 0.5), pfeil_ende=True, pfeil_anfang=True),
           "Gewinkelte Verbindung": _linie((0, 0.15), (0.5, 0.15), (0.5, 0.85), (1, 0.85)),
           "Gewinkelte Pfeilverbindung": _linie((0, 0.15), (0.5, 0.15), (0.5, 0.85), (1, 0.85), pfeil_ende=True),
           "Bogen": _bogen(0, 180)}

KATEGORIEN: list[tuple[str, dict[str, Pfad]]] = [
    ("Linie", _LINIEN),
    ("Rechteck", {"Rechteck": _rechteck, "Abgerundetes Rechteck": _abgerundet(),
                  "Ecke abgeschnitten": _poly((0, 0), (0.78, 0), (1, 0.22), (1, 1), (0, 1)),
                  "Zwei Ecken abgeschnitten": _poly((0.22, 0), (0.78, 0), (1, 0.22), (1, 1), (0, 1), (0, 0.22)),
                  "Diagonale Ecken abgeschnitten": _poly((0, 0), (0.78, 0), (1, 0.22), (1, 1), (0.22, 1), (0, 0.78)),
                  "Gefaltete Ecke": _poly((0, 0), (1, 0), (1, 0.75), (0.75, 1), (0, 1))}),
    ("Standardformen", {"Ellipse": _ellipse, "Dreieck": _poly((0.5, 0), (1, 1), (0, 1)), "Rechtwinkliges Dreieck": _poly((0, 0), (1, 1), (0, 1)),
                        "Parallelogramm": _poly((0.25, 0), (1, 0), (0.75, 1), (0, 1)), "Trapez": _poly((0.22, 0), (0.78, 0), (1, 1), (0, 1)),
                        "Raute": _poly((0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)), "Fünfeck": _vieleck(5), "Sechseck": _vieleck(6, 0),
                        "Siebeneck": _vieleck(7), "Achteck": _vieleck(8, 22.5), "Zehneck": _vieleck(10), "Zwölfeck": _vieleck(12),
                        "Kreuz": _poly((0.33, 0), (0.67, 0), (0.67, 0.33), (1, 0.33), (1, 0.67), (0.67, 0.67), (0.67, 1), (0.33, 1),
                                       (0.33, 0.67), (0, 0.67), (0, 0.33), (0.33, 0.33)),
                        "Zylinder": _zylinder, "Ring": _ring, "Herz": _herz, "Mond": _mond, "Smiley": _smiley, "Wolke": _wolke,
                        "Blitz": _poly((0.4, 0), (0.75, 0.38), (0.58, 0.45), (0.95, 1), (0.35, 0.58), (0.52, 0.5), (0.1, 0.12))}),
    ("Blockpfeile", {"Pfeil nach rechts": _poly((0, 0.25), (0.6, 0.25), (0.6, 0), (1, 0.5), (0.6, 1), (0.6, 0.75), (0, 0.75)),
                     "Pfeil nach links": _poly((1, 0.25), (0.4, 0.25), (0.4, 0), (0, 0.5), (0.4, 1), (0.4, 0.75), (1, 0.75)),
                     "Pfeil nach oben": _poly((0.25, 1), (0.25, 0.4), (0, 0.4), (0.5, 0), (1, 0.4), (0.75, 0.4), (0.75, 1)),
                     "Pfeil nach unten": _poly((0.25, 0), (0.25, 0.6), (0, 0.6), (0.5, 1), (1, 0.6), (0.75, 0.6), (0.75, 0)),
                     "Pfeil links und rechts": _poly((0, 0.5), (0.25, 0), (0.25, 0.25), (0.75, 0.25), (0.75, 0), (1, 0.5), (0.75, 1), (0.75, 0.75),
                                                     (0.25, 0.75), (0.25, 1)),
                     "Pfeil oben und unten": _poly((0.5, 0), (1, 0.25), (0.75, 0.25), (0.75, 0.75), (1, 0.75), (0.5, 1), (0, 0.75), (0.25, 0.75),
                                                   (0.25, 0.25), (0, 0.25)),
                     "Pfeil in vier Richtungen": _poly((0.5, 0), (0.65, 0.15), (0.58, 0.15), (0.58, 0.42), (0.85, 0.42), (0.85, 0.35), (1, 0.5),
                                                       (0.85, 0.65), (0.85, 0.58), (0.58, 0.58), (0.58, 0.85), (0.65, 0.85), (0.5, 1),
                                                       (0.35, 0.85), (0.42, 0.85), (0.42, 0.58), (0.15, 0.58), (0.15, 0.65), (0, 0.5),
                                                       (0.15, 0.35), (0.15, 0.42), (0.42, 0.42), (0.42, 0.15), (0.35, 0.15)),
                     "Fünfeck-Pfeil": _poly((0, 0), (0.7, 0), (1, 0.5), (0.7, 1), (0, 1)),
                     "Winkelpfeil": _poly((0, 0), (0.7, 0), (1, 0.5), (0.7, 1), (0, 1), (0.3, 0.5)),
                     "Eingekerbter Pfeil": _poly((0, 0.25), (0.6, 0.25), (0.6, 0), (1, 0.5), (0.6, 1), (0.6, 0.75), (0, 0.75), (0.15, 0.5))}),
    ("Formelformen", {"Plus": _poly((0.38, 0.1), (0.62, 0.1), (0.62, 0.38), (0.9, 0.38), (0.9, 0.62), (0.62, 0.62), (0.62, 0.9), (0.38, 0.9),
                                    (0.38, 0.62), (0.1, 0.62), (0.1, 0.38), (0.38, 0.38)),
                      "Minus": _poly((0.1, 0.38), (0.9, 0.38), (0.9, 0.62), (0.1, 0.62)),
                      "Mal": _poly((0.2, 0.1), (0.5, 0.4), (0.8, 0.1), (0.9, 0.2), (0.6, 0.5), (0.9, 0.8), (0.8, 0.9), (0.5, 0.6), (0.2, 0.9),
                                   (0.1, 0.8), (0.4, 0.5), (0.1, 0.2)),
                      "Gleich": lambda r: _poly((0.1, 0.2), (0.9, 0.2), (0.9, 0.42), (0.1, 0.42))(r).united(
                          _poly((0.1, 0.58), (0.9, 0.58), (0.9, 0.8), (0.1, 0.8))(r)),
                      "Geteilt durch": lambda r: _poly((0.1, 0.4), (0.9, 0.4), (0.9, 0.6), (0.1, 0.6))(r).united(
                          _ellipse(QRectF(r.left() + r.width() * 0.4, r.top(), r.width() * 0.2, r.height() * 0.2))).united(
                          _ellipse(QRectF(r.left() + r.width() * 0.4, r.top() + r.height() * 0.8, r.width() * 0.2, r.height() * 0.2)))}),
    ("Flussdiagramm", {"Prozess": _rechteck, "Alternativer Prozess": _abgerundet(0.25), "Verzweigung": _poly((0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)),
                       "Daten": _poly((0.2, 0), (1, 0), (0.8, 1), (0, 1)), "Dokument": _dokument, "Grenzstelle": _abgerundet(0.5),
                       "Vorbereitung": _poly((0.2, 0), (0.8, 0), (1, 0.5), (0.8, 1), (0.2, 1), (0, 0.5)),
                       "Manuelle Eingabe": _poly((0, 0.3), (1, 0), (1, 1), (0, 1)), "Manueller Vorgang": _poly((0, 0), (1, 0), (0.8, 1), (0.2, 1)),
                       "Verbindungsstelle": _ellipse, "Gespeicherte Daten": _zylinder, "Zusammenführen": _poly((0, 0), (1, 0), (0.5, 1)),
                       "Auszug": _poly((0.5, 0), (1, 1), (0, 1))}),
    ("Sterne und Banner", {"Stern mit 4 Zacken": _stern(4, 0.38), "Stern mit 5 Zacken": _stern(5), "Stern mit 6 Zacken": _stern(6, 0.55),
                           "Stern mit 8 Zacken": _stern(8, 0.6), "Stern mit 10 Zacken": _stern(10, 0.68), "Stern mit 12 Zacken": _stern(12, 0.72),
                           "Stern mit 16 Zacken": _stern(16, 0.78), "Stern mit 24 Zacken": _stern(24, 0.82), "Stern mit 32 Zacken": _stern(32, 0.85),
                           "Explosion": _poly((0.05, 0.3), (0.32, 0.28), (0.35, 0.02), (0.52, 0.22), (0.78, 0.05), (0.72, 0.32), (0.98, 0.4),
                                              (0.75, 0.55), (0.9, 0.85), (0.6, 0.72), (0.45, 0.98), (0.36, 0.72), (0.08, 0.8), (0.22, 0.55)),
                           "Welle": _welle}),
    ("Legenden", {"Rechteckige Legende": _legende(_rechteck), "Abgerundete Legende": _legende(_abgerundet()),
                  "Ovale Legende": _legende(_ellipse), "Wolkenlegende": _legende(_wolke)}),
]
_ALLE = {n: f for _k, formen in KATEGORIEN for n, f in formen.items()}


def namen() -> list[str]:
    return list(_ALLE)


def hat(name: str) -> bool:
    return name in _ALLE


def ist_linie(name: str) -> bool:
    return name in _LINIEN


def pfad(name: str, r: QRectF) -> QPainterPath:
    return _ALLE[name](r)
