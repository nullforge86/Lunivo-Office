"""Anbindung der Oberfläche an ``core.listen.aufzaehlungen.listen`` über ``framework.anbindung.listen``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import framework.anbindung.listen as _fw
from writer.werte import eigene_kopie


@cache
def nummerierungen():
    return eigene_kopie(_fw.nummerierungen())


@cache
def stile():
    return eigene_kopie(_fw.stile())


def liste(stil: str, praefix: str = '', suffix: str = '.', start: int = 1, zeichen: Mapping | None = None, pos: Mapping | None = None) -> Mapping:
    """``pos``: eigene Position der Nummer (``ausr``, ``ausr_art``, ``tab``, ``einzug`` in mm) — dann zeichnet Lunivo die Nummer selbst."""
    return eigene_kopie(_fw.liste(stil, praefix, suffix, start, zeichen, pos))


def marke(spec: Mapping) -> str | None:
    """Zeichenfolge für ``liste_zeichner`` (Vorschaubild) dieser Liste."""
    return eigene_kopie(_fw.marke(spec))


def zeichen_filtern(w: Mapping | None) -> Mapping:
    """Aus den Werten eines Schriftart-Fensters nur das, was für Nummern gilt und gesetzt ist."""
    return eigene_kopie(_fw.zeichen_filtern(w))
