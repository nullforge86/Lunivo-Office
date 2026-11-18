"""Kreisgrafiken des Diagrammzeichners (QPainter): 3D-Kreis, Kreis von Kreis, Balken von Kreis. Keine Oberfläche.

``zeichnen`` malt in das Zeichnungsbereich-Rechteck ``pa`` des Diagramms; die Scheiben von QtCharts sind dabei unsichtbar (Legende,
Titel und Geometrie bleiben die des Diagramms). Winkel: 0 Grad = 3 Uhr, im Uhrzeigersinn; Start der Scheiben bei 12 Uhr."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF

REST = QColor("#9aa0a6")


def _scheiben(werte: list[float], start: float = -90.0) -> list[tuple[float, float]]:
    """(Anfang, Spanne) in Grad je Wert, im Uhrzeigersinn ab ``start``."""
    summe = sum(abs(v) for v in werte) or 1.0
    out, a = [], start
    for v in werte:
        span = abs(v) / summe * 360.0
        out.append((a, span)); a += span
    return out


def _text(p: QPainter, mitte: QPointF, text: str, farbe: QColor) -> None:
    p.setPen(farbe)
    r = QRectF(0, 0, 80, 18); r.moveCenter(mitte)
    p.drawText(r, Qt.AlignCenter, text)


def _flach(p: QPainter, c: QPointF, r: float, werte, farben, beschriftung: bool, schrift: QColor, start: float = -90.0) -> list[tuple[float, float]]:
    sc = _scheiben(werte, start)
    rect = QRectF(c.x() - r, c.y() - r, 2 * r, 2 * r)
    p.setPen(QPen(QColor("white"), 1.2))
    for (a, span), f in zip(sc, farben):
        p.setBrush(f)
        p.drawPie(rect, int(round(-a * 16)), int(round(-span * 16)))
        if beschriftung and span > 12:
            m = math.radians(a + span / 2)
            _text(p, QPointF(c.x() + 0.65 * r * math.cos(m), c.y() + 0.65 * r * math.sin(m)), f"{abs(werte[sc.index((a, span))]):g}", QColor("white"))
    return sc


def _drei_d(p: QPainter, pa: QRectF, werte, farben, beschriftung: bool) -> None:
    kipp = 0.55
    rx = min(pa.width() * 0.46, pa.height() * 0.95 / (2 * kipp + 0.22))
    ry, tiefe = rx * kipp, rx * 0.22
    cx, cy = pa.center().x(), pa.center().y() - tiefe / 2
    sc = _scheiben(werte)

    def punkt(a: float, dy: float = 0.0) -> QPointF:
        return QPointF(cx + rx * math.cos(math.radians(a)), cy + ry * math.sin(math.radians(a)) + dy)

    def bogen(a: float, span: float) -> list[float]:
        n = max(2, int(span / 3) + 1)
        return [a + span * k / (n - 1) for k in range(n)]
    p.setPen(Qt.NoPen)
    for (a, span), f in zip(sc, farben):                        # Seitenfläche: nur der vordere Teil des Randes (unten) sichtbar
        w = bogen(a, span)
        for a0, a1 in zip(w, w[1:]):
            if math.sin(math.radians((a0 + a1) / 2)) <= 0:
                continue
            p.setBrush(f.darker(150))
            p.drawPolygon(QPolygonF([punkt(a0), punkt(a1), punkt(a1, tiefe), punkt(a0, tiefe)]))
    p.setPen(QPen(QColor("white"), 1.0))
    for (a, span), f, v in zip(sc, farben, werte):             # Deckfläche
        p.setBrush(f)
        p.drawPolygon(QPolygonF([QPointF(cx, cy)] + [punkt(x) for x in bogen(a, span)]))
        if beschriftung and span > 12:
            m = math.radians(a + span / 2)
            _text(p, QPointF(cx + 0.62 * rx * math.cos(m), cy + 0.62 * ry * math.sin(m)), f"{abs(v):g}", QColor("white"))


def _kleine_indizes(werte) -> list[int]:
    """Die Rubriken mit den kleinsten Beträgen, die zum Rest („Weitere“) zusammengefasst werden."""
    n = len(werte)
    return sorted(range(n), key=lambda i: abs(werte[i]))[:max(2, n // 3) if n > 2 else 1]


def _rest_ansatz(c1: QPointF, r1: float, a0: float, span0: float) -> tuple[QPointF, QPointF]:
    """Die beiden Randpunkte des Rest-Kreisstücks (oben, unten), von denen die Verbindungslinien ausgehen."""
    oben = QPointF(c1.x() + r1 * math.cos(math.radians(a0 + span0)), c1.y() + r1 * math.sin(math.radians(a0 + span0)))
    unten = QPointF(c1.x() + r1 * math.cos(math.radians(a0)), c1.y() + r1 * math.sin(math.radians(a0)))
    return (unten, oben) if oben.y() > unten.y() else (oben, unten)


def _von_kreis(p: QPainter, pa: QRectF, balken: bool, werte, farben, beschriftung: bool, schrift: QColor) -> None:
    klein = _kleine_indizes(werte)
    gross = [i for i in range(len(werte)) if i not in klein]
    rest = sum(abs(werte[i]) for i in klein)
    haupt = [werte[i] for i in gross] + [rest]
    # „Weitere“ mittig bei 3 Uhr: Start = Hälfte der Restspanne vor 3 Uhr, Reihenfolge: Rest zuerst gedreht
    summe = sum(abs(v) for v in haupt) or 1.0
    rest_span = rest / summe * 360.0
    r1 = min(pa.width() * 0.27, pa.height() * 0.44)
    c1 = QPointF(pa.left() + pa.width() * 0.29, pa.center().y())
    sc = _flach(p, c1, r1, haupt, [farben[i] for i in gross] + [REST], beschriftung, schrift, start=rest_span / 2)
    oben, unten = _rest_ansatz(c1, r1, *sc[-1])
    p.setPen(QPen(QColor("#9aa0a6"), 1)); p.setBrush(Qt.NoBrush)
    kl = [werte[i] for i in klein]
    if balken:
        _rest_balken(p, pa, oben, unten, r1, klein, kl, farben, beschriftung)
    else:
        _rest_kreis(p, pa, oben, unten, r1, klein, kl, farben, beschriftung, schrift)


def _rest_balken(p: QPainter, pa: QRectF, oben: QPointF, unten: QPointF, r1: float, klein, kl, farben, beschriftung: bool) -> None:
    """Gestapelter Balken für die zusammengefassten kleinen Werte, mit Verbindungslinien vom Hauptkreis."""
    bw, bh = pa.width() * 0.09, r1 * 1.5
    x0, y0 = pa.left() + pa.width() * 0.72, pa.center().y() - bh / 2
    p.drawLine(oben, QPointF(x0, y0)); p.drawLine(unten, QPointF(x0, y0 + bh))
    summe_k = sum(abs(v) for v in kl) or 1.0
    y = y0 + bh
    p.setPen(QPen(QColor("white"), 1.0))
    for i, v in zip(klein, kl):
        h = abs(v) / summe_k * bh
        p.setBrush(farben[i]); p.drawRect(QRectF(x0, y - h, bw, h))
        if beschriftung and h > 12:
            _text(p, QPointF(x0 + bw / 2, y - h / 2), f"{abs(v):g}", QColor("white"))
        y -= h


def _rest_kreis(p: QPainter, pa: QRectF, oben: QPointF, unten: QPointF, r1: float, klein, kl, farben, beschriftung: bool, schrift: QColor) -> None:
    """Zweiter Kreis für die zusammengefassten kleinen Werte, mit Verbindungslinien vom Hauptkreis."""
    r2 = r1 * 0.6
    c2 = QPointF(pa.left() + pa.width() * 0.78, pa.center().y())
    p.drawLine(oben, QPointF(c2.x(), c2.y() - r2)); p.drawLine(unten, QPointF(c2.x(), c2.y() + r2))
    _flach(p, c2, r2, kl, [farben[i] for i in klein], beschriftung, schrift)


def zeichnen(p: QPainter, pa: QRectF, u: str, kategorien: list[str], werte: list[float], farben: list[QColor], beschriftung: bool, schrift: QColor) -> None:
    """Malt die Kreisgrafik ``u`` (``kreis_3d`` | ``kreis_von_kreis`` | ``kreis_balken``) in ``pa``."""
    werte = [v for v in werte[:len(kategorien)]]
    farben = [farben[i % len(farben)] for i in range(len(werte))] if farben else [QColor("#4a8fd8")] * len(werte)
    if not werte or pa.width() < 20 or pa.height() < 20:
        return
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    if u == "kreis_3d":
        _drei_d(p, pa, werte, farben, beschriftung)
    else:
        _von_kreis(p, pa, u == "kreis_balken", werte, farben, beschriftung, schrift)
    p.restore()
