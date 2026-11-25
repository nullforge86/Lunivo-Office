"""Anbindung der Oberfläche an ``core.formatierung.absatz.tabfuell`` über ``framework.anbindung.tabfuell``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.tabfuell as _fw
from writer.werte import eigene_kopie


@cache
def fuell():
    return eigene_kopie(_fw.fuell())
