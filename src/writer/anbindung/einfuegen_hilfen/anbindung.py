"""Anbindung der Oberfläche an ``core.bearbeitung.einfuegen_hilfen`` über ``framework.anbindung.einfuegen_hilfen``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.einfuegen_hilfen as _fw
from writer.werte import eigene_kopie


@cache
def wordart_vorlagen():
    return eigene_kopie(_fw.wordart_vorlagen())
