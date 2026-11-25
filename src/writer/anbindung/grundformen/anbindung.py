"""Anbindung der Oberfläche an ``core.geometrie.grundformen`` über ``framework.anbindung.grundformen``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.grundformen as _fw
from writer.werte import eigene_kopie


@cache
def formen():
    return eigene_kopie(_fw.formen())
