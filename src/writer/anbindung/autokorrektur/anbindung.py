"""Anbindung der Oberfläche an ``core.korrektur.rechtschreibung.autokorrektur`` über ``framework.anbindung.autokorrektur``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.autokorrektur as _fw
from writer.werte import eigene_kopie


@cache
def schalter():
    return eigene_kopie(_fw.schalter())
