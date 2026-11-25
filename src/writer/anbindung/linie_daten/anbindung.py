"""Anbindung der Oberfläche an ``core.objekte.formen.linie_daten`` über ``framework.anbindung.linie_daten``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.linie_daten as _fw
from writer.werte import eigene_kopie


@cache
def alle_seiten():
    return eigene_kopie(_fw.alle_seiten())


@cache
def linienbreiten():
    return eigene_kopie(_fw.linienbreiten())


@cache
def objekt_striche():
    return eigene_kopie(_fw.objekt_striche())
