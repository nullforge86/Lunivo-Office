"""Anbindung der Oberfläche an ``core.objekte.wordart.textfx_daten`` über ``framework.anbindung.textfx_daten``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.textfx_daten as _fw
from writer.werte import eigene_kopie


@cache
def warp_formen():
    return eigene_kopie(_fw.warp_formen())


@cache
def bahnen():
    """Bahnen der Mehrfachlinien: (Abstand von der Mitte, Dicke) in Linienbreiten."""
    return eigene_kopie(_fw.bahnen())


def tiefe_faktor(mat: str, licht: str, t: float) -> float:
    """Helligkeitsfaktor einer Tiefenschicht ``t`` (0..1) nach Material und Beleuchtung."""
    return _fw.tiefe_faktor(mat, licht, t)
