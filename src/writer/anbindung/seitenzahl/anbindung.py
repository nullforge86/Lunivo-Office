"""Anbindung der Oberfläche an ``core.dokument.kopf_fusszeilen.seitenzahl`` über ``framework.anbindung.seitenzahl``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.seitenzahl as _fw
from writer.werte import eigene_kopie


@cache
def muster():
    return eigene_kopie(_fw.muster())


@cache
def positionen():
    return eigene_kopie(_fw.positionen())


@cache
def trenner():
    return eigene_kopie(_fw.trenner())


@cache
def vorgaben():
    return eigene_kopie(_fw.vorgaben())
