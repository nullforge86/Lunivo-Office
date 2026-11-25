"""Anbindung der Oberfläche an ``core.suche.textsuche.suche`` über ``framework.anbindung.suche``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.suche as _fw
from writer.werte import eigene_kopie


@cache
def spezial():
    return eigene_kopie(_fw.spezial())


@cache
def spezial_ersetzen():
    return eigene_kopie(_fw.spezial_ersetzen())
