"""Anbindung der Oberfläche an ``core.dokument.zusatz`` über ``framework.anbindung.zusatz``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.zusatz as _fw
from writer.werte import eigene_kopie


@cache
def ki_autor():
    return eigene_kopie(_fw.ki_autor())


def kommentar_farbe(geloest: bool = False) -> str:
    return eigene_kopie(_fw.kommentar_farbe(geloest))


def roemisch(n: int) -> str:
    return eigene_kopie(_fw.roemisch(n))
