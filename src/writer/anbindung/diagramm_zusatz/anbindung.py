"""Anbindung der Oberfläche an ``core.diagramme.daten.diagramm_zusatz`` über ``framework.anbindung.diagramm_zusatz``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import framework.anbindung.diagramm_zusatz as _fw
from writer.werte import eigene_kopie


@cache
def elemente():
    return eigene_kopie(_fw.elemente())


@cache
def element_namen():
    return eigene_kopie(_fw.element_namen())


@cache
def legenden_lagen():
    return eigene_kopie(_fw.legenden_lagen())


@cache
def standard_elemente():
    return eigene_kopie(_fw.standard_elemente())


def elemente_wirksam(d: Mapping) -> Mapping:
    """Alle neun Elemente mit ihrem Wert: Wahrheitswerte, bei ``legende`` die Lage (``oben`` … ``rechts``) oder ``aus``."""
    return eigene_kopie(_fw.elemente_wirksam(d))
