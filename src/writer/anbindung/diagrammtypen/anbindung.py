"""Anbindung der Oberfläche an ``core.layout.drucklayout.ausgabe.diagramm.diagrammtypen`` über ``framework.anbindung.diagrammtypen``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.diagrammtypen as _fw
from writer.werte import eigene_kopie


@cache
def alt():
    return eigene_kopie(_fw.alt())


@cache
def beispiel_kategorien():
    return eigene_kopie(_fw.beispiel_kategorien())


@cache
def beispiel_reihen():
    return eigene_kopie(_fw.beispiel_reihen())


@cache
def farben():
    return eigene_kopie(_fw.farben())


@cache
def kombi_typen():
    return eigene_kopie(_fw.kombi_typen())


@cache
def namen():
    return eigene_kopie(_fw.namen())


@cache
def typen():
    return eigene_kopie(_fw.typen())


@cache
def vorlagen():
    return eigene_kopie(_fw.vorlagen())
