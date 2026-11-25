"""Anbindung der Oberfläche an ``core.tabellen.modell.tabelleneigenschaften`` über ``framework.anbindung.tabelleneigenschaften``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.tabelleneigenschaften as _fw
from writer.werte import eigene_kopie


@cache
def vorgabe():
    return eigene_kopie(_fw.vorgabe())
