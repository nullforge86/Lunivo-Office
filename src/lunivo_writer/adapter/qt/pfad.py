"""Pfade zwischen Qt und dem Modell: ``QPainterPath`` → ``core.document.objekte.VectorPath`` (und zurück). Der Formenkatalog baut seine Umrisse mit Qt-Geometrie;
im Dokument steht dann der Vektorpfad ohne Qt, gezeichnet wird er vom Rendering-Backend."""
from __future__ import annotations

from PySide6.QtGui import QPainterPath

from lunivo_writer.core.document.objekte import VectorPath


def pfad_zu_vektor(pfad: QPainterPath) -> VectorPath:
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
    return VectorPath(tuple(ops))


def vektor_zu_pfad(v: VectorPath) -> QPainterPath:
    from lunivo_writer.adapter.qt.rendering import QtRenderBackend
    return QtRenderBackend._vereinigt(QtRenderBackend._pfade(list(v.ops)), False)
