"""Anbindung der Oberfläche an ``core.layout.drucklayout.ausgabe.objekte.linien`` über ``framework.anbindung.linien``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.linien as _fw
from writer.werte import eigene_kopie


@cache
def stile():
    return eigene_kopie(_fw.stile())
