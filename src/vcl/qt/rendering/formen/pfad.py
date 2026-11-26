"""Pfade zwischen Qt und der Oberfläche ohne Qt: ``QPainterPath`` → ``Vektorpfad`` (Pfadanweisungen, ``writer.werte``) und zurück. Der Formenkatalog baut
seine Umrisse mit Qt-Geometrie; ins Dokument gehen nur die Pfadanweisungen, gezeichnet werden sie vom Kern."""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QPainterPath

from writer.werte import Vektorpfad


def pfad_zu_vektor(pfad: QPainterPath) -> Vektorpfad:
    ops: list[tuple] = []
    i, n = 0, pfad.elementCount()
    while i < n:
        e = pfad.elementAt(i)
        if e.isMoveTo():
            ops.append(("M", e.x, e.y))
        elif e.isLineTo():
            ops.append(("L", e.x, e.y))
        elif e.isCurveTo() and i + 2 < n:
            c2, ende = pfad.elementAt(i + 1), pfad.elementAt(i + 2)
            ops.append(("C", e.x, e.y, c2.x, c2.y, ende.x, ende.y))
            i += 2
        i += 1
    return Vektorpfad(tuple(ops))


def _pfade(ops: list) -> list[QPainterPath]:
    """Teilpfade der Anweisungen: ein neues ``M``, ``E`` oder ``R`` beginnt einen eigenen Pfad."""
    pfade: list[QPainterPath] = []
    aktuell: QPainterPath | None = None
    for op in ops:
        k = op[0]
        if k == "M":
            aktuell = QPainterPath(QPointF(op[1], op[2]))
            pfade.append(aktuell)
        elif k == "L" and aktuell is not None:
            aktuell.lineTo(op[1], op[2])
        elif k == "Q" and aktuell is not None:
            aktuell.quadTo(QPointF(op[1], op[2]), QPointF(op[3], op[4]))
        elif k == "C" and aktuell is not None:
            aktuell.cubicTo(*op[1:7])
        elif k == "Z" and aktuell is not None:
            aktuell.closeSubpath()
        elif k == "E":
            pf = QPainterPath()
            pf.addEllipse(QPointF(op[1], op[2]), op[3], op[4])
            pfade.append(pf)
        elif k == "R":
            pf = QPainterPath()
            pf.addRect(QRectF(op[1], op[2], op[3], op[4]))
            pfade.append(pf)
    return pfade


def vektor_zu_pfad(v) -> QPainterPath:
    """Die Pfadanweisungen ``v.ops`` als ein ``QPainterPath`` (alle Teilpfade zusammen, ohne sie zu vereinigen)."""
    pf = QPainterPath()
    for t in _pfade(list(v.ops)):
        pf.addPath(t)
    return pf
