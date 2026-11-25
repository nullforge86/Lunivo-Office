"""Anbindung der Oberfläche an ``core.objekte.formen.formen_daten`` über ``framework.anbindung.formen_daten``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import framework.anbindung.formen_daten as _fw
from writer.werte import eigene_kopie


@cache
def gruppen_abstand():
    return eigene_kopie(_fw.gruppen_abstand())


@cache
def standard():
    return eigene_kopie(_fw.standard())


@cache
def vorlagen():
    return eigene_kopie(_fw.vorlagen())


def form_daten(o: Mapping, breite: float, hoehe: float) -> Mapping:
    return eigene_kopie(_fw.form_daten(o, breite, hoehe))
