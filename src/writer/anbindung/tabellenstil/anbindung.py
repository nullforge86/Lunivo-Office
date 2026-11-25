"""Anbindung der Oberfläche an ``core.tabellen.formatierung.tabellenstil`` über ``framework.anbindung.tabellenstil``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.tabellenstil as _fw
from writer.werte import eigene_kopie


@cache
def vorlagen():
    return eigene_kopie(_fw.vorlagen())
