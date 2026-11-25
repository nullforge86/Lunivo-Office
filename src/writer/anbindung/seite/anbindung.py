"""Anbindung der Oberfläche an ``core.dokument.abschnitte.seite`` über ``framework.anbindung.seite``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.seite as _fw
from writer.werte import eigene_kopie


@cache
def paper_mm():
    return eigene_kopie(_fw.paper_mm())
