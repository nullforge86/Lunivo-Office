"""Anbindung der Oberfläche an ``core.objekte.formen.freie_bilder_daten`` über ``framework.anbindung.freie_bilder_daten``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.freie_bilder_daten as _fw
from writer.werte import eigene_kopie


@cache
def max_bildpunkte():
    return eigene_kopie(_fw.max_bildpunkte())


@cache
def schema():
    return eigene_kopie(_fw.schema())
