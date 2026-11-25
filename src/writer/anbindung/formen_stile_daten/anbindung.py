"""Anbindung der Oberfläche an ``core.objekte.formen.formen_stile_daten`` über ``framework.anbindung.formen_stile_daten``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.formen_stile_daten as _fw
from writer.werte import eigene_kopie


@cache
def spalten():
    return eigene_kopie(_fw.spalten())


@cache
def zeilen():
    return eigene_kopie(_fw.zeilen())
