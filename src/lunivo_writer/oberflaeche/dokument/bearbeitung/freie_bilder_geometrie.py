"""Maße und reine Geometrie der frei positionierten Bilder im Editor (Griffe, Rahmen, Anpassungsgriffe) — kein Zeichnen, keine Maus, kein Zustand.

Gebraucht von ``freie_bilder_zeichnen.py`` (Darstellung), ``freie_bilder_interaktion.py`` (Maus und Tastatur) und ``freie_bilder_bedienung.py``
(Zusammensetzung des ``FreieBilderMixin``). Die Maße stehen hier einmal; Farben kommen aus ``kern/farben.Farbe``.
"""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QTransform

# Sinnbilder des Formleisten-Schwebeknopfs und der Anpassungsraute: bewusst fest (Gruppe C)
SINNBILD_GELB, SINNBILD_GELB_HELL, SINNBILD_KONTUR = "#f2c200", "#ffe45c", "#1c3faa"
GRIFF = 9.0                                                  # Seitenlänge eines Griffs in Bildschirmpunkten
GRIFFE = {"nw": (0, 0), "n": (0.5, 0), "ne": (1, 0), "e": (1, 0.5), "se": (1, 1), "s": (0.5, 1), "sw": (0, 1), "w": (0, 0.5)}
ROT_ABSTAND = 24.0                                           # Drehgriff: so weit über der Oberkante des Rahmens
CURSOR = {"rot": Qt.PointingHandCursor, "adj": Qt.PointingHandCursor, "nw": Qt.SizeFDiagCursor, "se": Qt.SizeFDiagCursor, "ne": Qt.SizeBDiagCursor, "sw": Qt.SizeBDiagCursor,
          "n": Qt.SizeVerCursor, "s": Qt.SizeVerCursor, "e": Qt.SizeHorCursor, "w": Qt.SizeHorCursor}
MIN_GROESSE = 8                                              # kleinste Breite/Höhe beim Ziehen an einem Griff (Blattpunkte)


def griff_mitte(r: QRectF, name: str) -> QPointF:
    """Mitte des Griffs ``name`` (acht Größengriffe oder ``rot``) am Rahmen ``r``."""
    if name == "rot":
        return QPointF(r.center().x(), r.top() - ROT_ABSTAND)
    fx, fy = GRIFFE[name]
    return QPointF(r.left() + r.width() * fx, r.top() + r.height() * fy)


def abbilden(r: QRectF, a: dict, rr: QRectF) -> QRectF:
    """Ein Rechteck in logischen Bildpunkten des Objekts (Breite ``b`` × Höhe ``h``) in Editor-Koordinaten (Zoom, Lage) umrechnen."""
    sx, sy = r.width() / max(1.0, float(a["b"])), r.height() / max(1.0, float(a["h"]))
    return QRectF(r.x() + rr.x() * sx, r.y() + rr.y() * sy, rr.width() * sx, rr.height() * sy)


def um_mitte_drehen(punkt: QPointF, r: QRectF, grad: float) -> QPointF:
    """Ein Punkt um die Mitte von ``r`` um ``grad`` Grad gedreht."""
    return QTransform().translate(r.center().x(), r.center().y()).rotate(grad).translate(-r.center().x(), -r.center().y()).map(punkt)


def adj_lagen(r: QRectF, a: dict | None, vorlaeufig: tuple[int, float] | None = None) -> dict[str, QPointF]:
    """Lage der Anpassungsgriffe (gelbe Raute) einer Form in Editor-Koordinaten: {"adj0": Punkt, …}; leer bei anderen Objekten.
    ``vorlaeufig``: (Nummer, Wert) des Griffs, der gerade gezogen wird."""
    if a is None or a.get("art") != "form":
        return {}
    from lunivo_writer.editor.objekte import formen as F
    d = a.get("daten") or {}
    form = d.get("form", "Rechteck")
    adj = d.get("adj")
    if vorlaeufig is not None:
        adj = F.anpassen(form, vorlaeufig[1], adj, vorlaeufig[0])
    dreh = float(a.get("dreh", 0.0) or 0.0)
    out = {}
    for i in range(len(F.anpass_griffe(form, QRectF(0, 0, 1, 1)))):
        c = F.anpass_griff(form, QRectF(r), adj, i)
        if c is None:
            continue
        out[f"adj{i}"] = um_mitte_drehen(c, r, dreh) if dreh else c
    return out


def drehwinkel(mitte: QPointF, pos: QPointF, raster: bool) -> float:
    """Der Winkel (Grad, 0 = oben) von der Mitte zur Maus; ``raster``: auf 15 Grad gerundet."""
    w = math.degrees(math.atan2(pos.x() - mitte.x(), mitte.y() - pos.y())) % 360.0
    return round(w / 15.0) * 15.0 % 360.0 if raster else w


def _kanten_verschieben(r: QRectF, griff: str, dx: float, dy: float) -> tuple[float, float, float, float]:
    l, t, rr, b = r.left(), r.top(), r.right(), r.bottom()
    if "w" in griff:
        l = min(l + dx, rr - MIN_GROESSE)
    if "e" in griff:
        rr = max(rr + dx, l + MIN_GROESSE)
    if "n" in griff:
        t = min(t + dy, b - MIN_GROESSE)
    if "s" in griff:
        b = max(b + dy, t + MIN_GROESSE)
    return l, t, rr, b


def groesse_rechteck(r: QRectF, griff: str, dx: float, dy: float, frei: bool) -> QRectF:
    """Das Rechteck ``r`` nach dem Ziehen am Griff ``griff`` um (``dx``, ``dy``); ohne ``frei`` bleibt das Seitenverhältnis erhalten."""
    verhaeltnis = r.width() / max(1.0, r.height())
    l, t, rr, b = _kanten_verschieben(r, griff, dx, dy)
    if not frei and griff in ("n", "s"):                             # gesperrt, obere/untere Kante: die Höhe bestimmt die Breite
        rr = l + (b - t) * verhaeltnis
    elif not frei:                                                   # Ecke: Seitenverhältnis halten, Breite bestimmt die Höhe
        hoehe = (rr - l) / verhaeltnis
        if "n" in griff:
            t = b - hoehe
        else:
            b = t + hoehe
    return QRectF(l, t, rr - l, b - t)
