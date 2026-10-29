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

# ---- Weitere Formen (Ergänzung der Gruppen nach der Vorlage) ---------------------------------------------------------------------
def _pt(r: QRectF, x: float, y: float) -> QPointF:
    return QPointF(r.left() + x * r.width(), r.top() + y * r.height())


def _spitze(p: QPainterPath, spitze: QPointF, davor: QPointF, lg: float) -> None:
    w = math.atan2(spitze.y() - davor.y(), spitze.x() - davor.x())
    for d in (2.6, -2.6):
        p.moveTo(spitze); p.lineTo(spitze.x() + lg * math.cos(w + d), spitze.y() + lg * math.sin(w + d))


def _kurve(ende: bool = False, anfang: bool = False) -> Pfad:
    def f(r: QRectF) -> QPainterPath:
        p = QPainterPath(_pt(r, 0, 0.15)); p.cubicTo(_pt(r, 0.5, 0.15), _pt(r, 0.5, 0.85), _pt(r, 1, 0.85))
        lg = min(r.width(), r.height()) * 0.18 + 4
        if ende:
            _spitze(p, _pt(r, 1, 0.85), _pt(r, 0.5, 0.85), lg)
        if anfang:
            _spitze(p, _pt(r, 0, 0.15), _pt(r, 0.5, 0.15), lg)
        return p
    return f


def _vereint(*pfade: Pfad) -> Pfad:
    def f(r: QRectF) -> QPainterPath:
        p = pfade[0](r)
        for q in pfade[1:]:
            p = p.united(q(r))
        return p
    return f


def _mit_linien(grund: Pfad, *linien: tuple[tuple[float, float], tuple[float, float]]) -> Pfad:
    def f(r: QRectF) -> QPainterPath:
        p = grund(r)
        for a, b in linien:
            p.moveTo(_pt(r, *a)); p.lineTo(_pt(r, *b))
        return p
    return f


def _runde_ecken(tl: float, tr: float, br: float, bl: float) -> Pfad:
    def f(r: QRectF) -> QPainterPath:
        m = min(r.width(), r.height()); x0, y0, x1, y1 = r.left(), r.top(), r.right(), r.bottom()
        a, b, c, d = (v * m for v in (tl, tr, br, bl))
        p = QPainterPath(); p.moveTo(x0 + a, y0); p.lineTo(x1 - b, y0)
        p.arcTo(QRectF(x1 - 2 * b, y0, 2 * b, 2 * b), 90, -90) if b else p.lineTo(x1, y0)
        p.lineTo(x1, y1 - c)
        p.arcTo(QRectF(x1 - 2 * c, y1 - 2 * c, 2 * c, 2 * c), 0, -90) if c else p.lineTo(x1, y1)
        p.lineTo(x0 + d, y1)
        p.arcTo(QRectF(x0, y1 - 2 * d, 2 * d, 2 * d), 270, -90) if d else p.lineTo(x0, y1)
        p.lineTo(x0, y0 + a)
        p.arcTo(QRectF(x0, y0, 2 * a, 2 * a), 180, -90) if a else p.lineTo(x0, y0)
        p.closeSubpath()
        return p
    return f


def _rahmen(r: QRectF) -> QPainterPath:
    p = _rechteck(r); i = QPainterPath(); d = min(r.width(), r.height()) * 0.2
    i.addRect(r.adjusted(d, d, -d, -d))
    return p.subtracted(i)


def _wuerfel(r: QRectF) -> QPainterPath:
    p = QPainterPath()
    for pts in (((0, 0.25), (0.75, 0.25), (0.75, 1), (0, 1)), ((0, 0.25), (0.25, 0), (1, 0), (0.75, 0.25)), ((0.75, 0.25), (1, 0), (1, 0.75), (0.75, 1))):
        p.addPolygon(QPolygonF([_pt(r, *q) for q in pts])); p.closeSubpath()
    return p


def _abgeschraegt(r: QRectF) -> QPainterPath:
    p = _rechteck(r); p.addRect(r.adjusted(r.width() * 0.15, r.height() * 0.15, -r.width() * 0.15, -r.height() * 0.15))
    for a, b in (((0, 0), (0.15, 0.15)), ((1, 0), (0.85, 0.15)), ((1, 1), (0.85, 0.85)), ((0, 1), (0.15, 0.85))):
        p.moveTo(_pt(r, *a)); p.lineTo(_pt(r, *b))
    return p


def _sektor(r: QRectF) -> QPainterPath:
    p = QPainterPath(); p.moveTo(r.center()); p.arcTo(r, 0, 270); p.closeSubpath()
    return p


def _sehne(r: QRectF) -> QPainterPath:
    p = QPainterPath(); p.arcMoveTo(r, 45); p.arcTo(r, 45, 270); p.closeSubpath()
    return p


def _tropfen(r: QRectF) -> QPainterPath:
    p = QPainterPath(_pt(r, 0.5, 0))
    p.cubicTo(_pt(r, 0.5, 0.2), _pt(r, 1, 0.4), _pt(r, 1, 0.65)); p.cubicTo(_pt(r, 1, 0.9), _pt(r, 0.75, 1), _pt(r, 0.5, 1))
    p.cubicTo(_pt(r, 0.25, 1), _pt(r, 0, 0.9), _pt(r, 0, 0.65)); p.cubicTo(_pt(r, 0, 0.4), _pt(r, 0.5, 0.2), _pt(r, 0.5, 0))
    return p


def _sonne(r: QRectF) -> QPainterPath:
    p = _ellipse(QRectF(_pt(r, 0.28, 0.28), _pt(r, 0.72, 0.72)))
    for i in range(8):
        w = math.radians(i * 45)
        p.moveTo(_pt(r, 0.5 + 0.3 * math.cos(w), 0.5 + 0.3 * math.sin(w))); p.lineTo(_pt(r, 0.5 + 0.48 * math.cos(w), 0.5 + 0.48 * math.sin(w)))
    return p


def _blockbogen(r: QRectF) -> QPainterPath:
    a = QRectF(r.left(), r.top(), r.width(), 2 * r.height()); i = QRectF(r.left() + r.width() * 0.25, r.top() + r.height() * 0.5, r.width() * 0.5, r.height())
    p = QPainterPath(); p.arcMoveTo(a, 0); p.arcTo(a, 0, 180); p.arcTo(i, 180, -180); p.closeSubpath()
    return p


def _verbot(r: QRectF) -> QPainterPath:
    p = _ring(r); c = r.center(); rx, ry = r.width() / 2, r.height() / 2; k = math.sqrt(0.5)
    bar = QPainterPath(); bar.addPolygon(QPolygonF([QPointF(c.x() - rx * k, c.y() - ry * k * 0.75), QPointF(c.x() - rx * k * 0.75, c.y() - ry * k),
                                                    QPointF(c.x() + rx * k, c.y() + ry * k * 0.75), QPointF(c.x() + rx * k * 0.75, c.y() + ry * k)]))
    return p.united(bar)


def _eckig(links: bool) -> Pfad:
    return _linie((1, 0), (0, 0), (0, 1), (1, 1)) if links else _linie((0, 0), (1, 0), (1, 1), (0, 1))


def _geschweift(links: bool) -> Pfad:
    def f(r: QRectF) -> QPainterPath:
        s = (lambda x: x) if links else (lambda x: 1 - x)
        p = QPainterPath(_pt(r, s(1), 0)); p.cubicTo(_pt(r, s(0.5), 0), _pt(r, s(0.5), 0.2), _pt(r, s(0.5), 0.35))
        p.lineTo(_pt(r, s(0.5), 0.4)); p.cubicTo(_pt(r, s(0.5), 0.47), _pt(r, s(0.35), 0.5), _pt(r, s(0), 0.5))
        p.cubicTo(_pt(r, s(0.35), 0.5), _pt(r, s(0.5), 0.53), _pt(r, s(0.5), 0.6)); p.lineTo(_pt(r, s(0.5), 0.65))
        p.cubicTo(_pt(r, s(0.5), 0.8), _pt(r, s(0.5), 1), _pt(r, s(1), 1))
        return p
    return f


def _drehe(punkte, n: int):
    """Punktliste (Anteile) um n × 90° im Uhrzeigersinn drehen."""
    for _ in range(n % 4):
        punkte = [(1 - y, x) for x, y in punkte]
    return punkte


_BESCHRIFTUNG = [(0, 0.15), (0.5, 0.15), (0.5, 0.3), (0.75, 0.3), (0.75, 0), (1, 0.5), (0.75, 1), (0.75, 0.7), (0.5, 0.7), (0.5, 0.85), (0, 0.85)]
_DREI = [(0.5, 0), (0.7, 0.2), (0.58, 0.2), (0.58, 0.42), (0.8, 0.42), (0.8, 0.3), (1, 0.5), (0.8, 0.7), (0.8, 0.58), (0.58, 0.58), (0.58, 1),
         (0.42, 1), (0.42, 0.58), (0.2, 0.58), (0.2, 0.7), (0, 0.5), (0.2, 0.3), (0.2, 0.42), (0.42, 0.42), (0.42, 0.2), (0.3, 0.2)]


def _kreispfeil(r: QRectF) -> QPainterPath:
    a = r.adjusted(r.width() * 0.1, r.height() * 0.1, -r.width() * 0.1, -r.height() * 0.1)
    p = QPainterPath(); p.arcMoveTo(a, 90); p.arcTo(a, 90, -270)
    e = p.currentPosition(); lg = min(r.width(), r.height()) * 0.2
    p.moveTo(e); p.lineTo(e.x() - lg, e.y() + lg); p.moveTo(e); p.lineTo(e.x() + lg, e.y() + lg)
    return p


def _ungleich(r: QRectF) -> QPainterPath:
    p = KATEGORIEN[4][1]["Gleich"](r)
    p.addPolygon(QPolygonF([_pt(r, 0.62, 0.05), _pt(r, 0.74, 0.1), _pt(r, 0.38, 0.95), _pt(r, 0.26, 0.9)])); p.closeSubpath()
    return p




def _verzoegerung(r: QRectF) -> QPainterPath:
    p = QPainterPath(r.topLeft()); p.lineTo(_pt(r, 0.5, 0)); p.arcTo(QRectF(r.left(), r.top(), r.width(), r.height()), 90, -180)
    p.lineTo(r.bottomLeft()); p.closeSubpath()
    return p


def _anzeige(r: QRectF) -> QPainterPath:
    p = QPainterPath(_pt(r, 0, 0.5)); p.lineTo(_pt(r, 0.2, 0)); p.lineTo(_pt(r, 0.75, 0))
    p.arcTo(QRectF(r.left() + r.width() * 0.5, r.top(), r.width() * 0.5, r.height()), 90, -180); p.lineTo(_pt(r, 0.2, 1)); p.closeSubpath()
    return p


def _mehrere_dokumente(r: QRectF) -> QPainterPath:
    p = QPainterPath()
    for dx, dy in ((0.12, 0), (0.06, 0.06), (0, 0.12)):
        p = p.united(_dokument(QRectF(r.left() + dx * r.width(), r.top() + dy * r.height(), r.width() * 0.88, r.height() * 0.82)))
    return p


def _knoten(kreuz: bool) -> Pfad:
    k = math.sqrt(0.5) * 0.5
    return _mit_linien(_ellipse, ((0.5, 0), (0.5, 1)), ((0, 0.5), (1, 0.5))) if kreuz else \
        _mit_linien(_ellipse, ((0.5 - k, 0.5 - k), (0.5 + k, 0.5 + k)), ((0.5 + k, 0.5 - k), (0.5 - k, 0.5 + k)))


def _doppelwelle(r: QRectF) -> QPainterPath:
    p = QPainterPath(_pt(r, 0, 0.2)); p.cubicTo(_pt(r, 0.17, -0.05), _pt(r, 0.33, 0.45), _pt(r, 0.5, 0.2)); p.cubicTo(_pt(r, 0.67, -0.05), _pt(r, 0.83, 0.45), _pt(r, 1, 0.2))
    p.lineTo(_pt(r, 1, 0.8)); p.cubicTo(_pt(r, 0.83, 1.05), _pt(r, 0.67, 0.55), _pt(r, 0.5, 0.8)); p.cubicTo(_pt(r, 0.33, 1.05), _pt(r, 0.17, 0.55), _pt(r, 0, 0.8))
    p.closeSubpath()
    return p


def _schriftrolle(waagerecht: bool) -> Pfad:
    def f(r: QRectF) -> QPainterPath:
        p = QPainterPath()
        if waagerecht:
            p.addRect(_rf(r, 0.08, 0.1, 0.92, 0.9)); p.addEllipse(_rf(r, 0, 0.05, 0.16, 0.95)); p.addEllipse(_rf(r, 0.84, 0.05, 1, 0.95))
        else:
            p.addRect(_rf(r, 0.1, 0.08, 0.9, 0.92)); p.addEllipse(_rf(r, 0.05, 0, 0.95, 0.16)); p.addEllipse(_rf(r, 0.05, 0.84, 0.95, 1))
        return p
    return f


def _rf(r: QRectF, x0: float, y0: float, x1: float, y1: float) -> QRectF:
    return QRectF(_pt(r, x0, y0), _pt(r, x1, y1))


def _linienlegende(var: int, balken: bool, rahmen: bool) -> Pfad:
    ende = {1: [(0.65, 0.3), (1, 1)], 2: [(0.65, 0.3), (0.85, 0.3), (1, 1)], 3: [(0.65, 0.3), (0.8, 0.3), (0.8, 0.7), (1, 1)]}[var]
    def f(r: QRectF) -> QPainterPath:
        p = QPainterPath()
        if rahmen:
            p.addRect(_rf(r, 0, 0, 0.65, 0.6))
        if balken:
            p.moveTo(_pt(r, 0.65, 0)); p.lineTo(_pt(r, 0.65, 0.6))
        p.moveTo(_pt(r, *ende[0]))
        for q in ende[1:]:
            p.lineTo(_pt(r, *q))
        return p
    return f


_LINIEN.update({"Schräge Linie": _linie((0, 0), (1, 1)), "Schräger Pfeil": _linie((0, 0), (1, 1), pfeil_ende=True),
                "Schräger Doppelpfeil": _linie((0, 0), (1, 1), pfeil_ende=True, pfeil_anfang=True),
                "Gewinkelte Doppelpfeilverbindung": _linie((0, 0.15), (0.5, 0.15), (0.5, 0.85), (1, 0.85), pfeil_ende=True, pfeil_anfang=True),
                "Gebogene Verbindung": _kurve(), "Gebogene Pfeilverbindung": _kurve(True), "Gebogene Doppelpfeilverbindung": _kurve(True, True)})
_ERGAENZUNG = {
    "Rechteck": {"Eine Ecke abgerundet": _runde_ecken(0, 0.3, 0, 0), "Zwei Ecken abgerundet": _runde_ecken(0.3, 0.3, 0, 0),
                 "Diagonale Ecken abgerundet": _runde_ecken(0.3, 0, 0.3, 0),
                 "Alle Ecken abgeschnitten": _poly((0.15, 0), (0.85, 0), (1, 0.15), (1, 0.85), (0.85, 1), (0.15, 1), (0, 0.85), (0, 0.15))},
    "Standardformen": {"Rahmen": _rahmen, "Halber Rahmen": _poly((0, 0), (1, 0), (0.7, 0.3), (0.3, 0.3), (0.3, 0.7), (0, 1)),
                       "L-Form": _poly((0, 0), (0.4, 0), (0.4, 0.6), (1, 0.6), (1, 1), (0, 1)),
                       "Diagonaler Streifen": _poly((0.5, 0), (1, 0), (0, 1), (0, 0.5)), "Abgeschrägtes Rechteck": _abgeschraegt, "Würfel": _wuerfel,
                       "Sektor": _sektor, "Sehne": _sehne, "Tropfen": _tropfen, "Sonne": _sonne, "Blockbogen": _blockbogen, "Verbotsschild": _verbot},
    "Blockpfeile": {"Abbiegender Pfeil": _poly((0, 1), (0, 0.25), (0.6, 0.25), (0.6, 0), (1, 0.4), (0.6, 0.8), (0.6, 0.55), (0.25, 0.55), (0.25, 1)),
                    "U-Pfeil": _poly((0, 1), (0, 0.3), (0.25, 0), (0.6, 0), (0.85, 0.3), (1, 0.3), (0.78, 0.7), (0.55, 0.3), (0.7, 0.3), (0.55, 0.15),
                                     (0.3, 0.15), (0.25, 0.3), (0.25, 1)),
                    "Pfeil in drei Richtungen": _poly(*_DREI),
                    "Gestreifter Pfeil": _vereint(_poly((0.25, 0.25), (0.6, 0.25), (0.6, 0), (1, 0.5), (0.6, 1), (0.6, 0.75), (0.25, 0.75)),
                                                  _poly((0, 0.25), (0.08, 0.25), (0.08, 0.75), (0, 0.75)), _poly((0.12, 0.25), (0.2, 0.25), (0.2, 0.75), (0.12, 0.75))),
                    "Beschriftungspfeil rechts": _poly(*_BESCHRIFTUNG), "Beschriftungspfeil unten": _poly(*_drehe(_BESCHRIFTUNG, 1)),
                    "Beschriftungspfeil links": _poly(*[(1 - x, y) for x, y in _BESCHRIFTUNG]), "Beschriftungspfeil oben": _poly(*_drehe(_BESCHRIFTUNG, 3)),
                    "Kreispfeil": _kreispfeil},
    "Formelformen": {"Ungleich": _ungleich},
    "Flussdiagramm": {"Vordefinierter Prozess": _mit_linien(_rechteck, ((0.12, 0), (0.12, 1)), ((0.88, 0), (0.88, 1))),
                      "Interne Speicherung": _mit_linien(_rechteck, ((0.12, 0), (0.12, 1)), ((0, 0.14), (1, 0.14))),
                      "Mehrere Dokumente": _mehrere_dokumente, "Verweis auf andere Seite": _poly((0, 0), (1, 0), (1, 0.6), (0.5, 1), (0, 0.6)),
                      "Karte": _poly((0.2, 0), (1, 0), (1, 1), (0, 1), (0, 0.2)), "Lochstreifen": _welle, "Summationsknoten": _knoten(False),
                      "ODER": _knoten(True), "Sortieren": _mit_linien(_poly((0.5, 0), (1, 0.5), (0.5, 1), (0, 0.5)), ((0, 0.5), (1, 0.5))),
                      "Sanduhr": _poly((0, 0), (1, 0), (0, 1), (1, 1)), "Verzögerung": _verzoegerung, "Anzeige": _anzeige},
    "Sterne und Banner": {"Stern mit 7 Zacken": _stern(7, 0.58), "Explosion 2": _poly((0, 0.4), (0.25, 0.3), (0.2, 0.05), (0.45, 0.22), (0.6, 0), (0.7, 0.25),
                                                                                       (0.95, 0.15), (0.85, 0.4), (1, 0.55), (0.8, 0.65), (0.9, 0.95),
                                                                                       (0.6, 0.8), (0.5, 1), (0.38, 0.8), (0.12, 0.95), (0.2, 0.68)),
                          "Doppelte Welle": _doppelwelle, "Horizontale Schriftrolle": _schriftrolle(True), "Vertikale Schriftrolle": _schriftrolle(False),
                          "Band": _poly((0, 0.25), (0.18, 0.25), (0.18, 0.1), (0.82, 0.1), (0.82, 0.25), (1, 0.25), (0.9, 0.5), (1, 0.75), (0.82, 0.75),
                                        (0.82, 0.9), (0.18, 0.9), (0.18, 0.75), (0, 0.75), (0.1, 0.5))},
    "Legenden": {f"Linienlegende{t} {v}": _linienlegende(v, b, rh) for t, b, rh in (("", False, True), (" mit Balken", True, True), (" ohne Rahmen", False, False))
                 for v in (1, 2, 3)},
}
_ERGAENZUNG["Standardformen"].update({"Eckige Klammer links": _eckig(True), "Eckige Klammer rechts": _eckig(False),
                                      "Geschweifte Klammer links": _geschweift(True), "Geschweifte Klammer rechts": _geschweift(False)})
for _g, _f in KATEGORIEN:
    _f.update(_ERGAENZUNG.get(_g, {}))
_OFFEN = {"Eckige Klammer links", "Eckige Klammer rechts", "Geschweifte Klammer links", "Geschweifte Klammer rechts", "Kreispfeil",
          "Linienlegende ohne Rahmen 1", "Linienlegende ohne Rahmen 2", "Linienlegende ohne Rahmen 3"}

_ALLE = {n: f for _k, formen in KATEGORIEN for n, f in formen.items()}


VOREINSTELLUNG = ["Linie", "Pfeil", "Rechteck", "Ellipse", "Dreieck", "Pfeil nach rechts", "Stern mit 5 Zacken", "Rechteckige Legende"]


def zuletzt(name: str) -> None:
    """Gruppe „Voreinstellung“ der Galerie: die zuletzt gewählten Formen stehen vorn (höchstens 16)."""
    if name in _ALLE:
        if name in VOREINSTELLUNG:
            VOREINSTELLUNG.remove(name)
        VOREINSTELLUNG.insert(0, name); del VOREINSTELLUNG[16:]


def namen() -> list[str]:
    return list(_ALLE)


def hat(name: str) -> bool:
    return name in _ALLE


def ist_linie(name: str) -> bool:
    return name in _LINIEN or name in _OFFEN


def pfad(name: str, r: QRectF) -> QPainterPath:
    return _ALLE[name](r)
