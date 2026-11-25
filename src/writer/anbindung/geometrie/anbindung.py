"""Anbindung der Oberfläche an ``core.layout.drucklayout.geometrie`` über ``framework.anbindung.geometrie``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.geometrie as _fw
from writer.werte import eigene_kopie


@cache
def blatt_abstand_px():
    return eigene_kopie(_fw.blatt_abstand_px())
