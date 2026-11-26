"""Anbindung der Oberfläche an ``core.objekte.formen.bildeffekte_daten`` über ``framework.anbindung.bildeffekte_daten``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import framework.anbindung.bildeffekte_daten as _fw
from writer.werte import eigene_kopie


@cache
def px_pt():
    return eigene_kopie(_fw.px_pt())


def hat_abschluss(fx: Mapping | None) -> bool:
    return eigene_kopie(_fw.hat_abschluss(fx))


def tiefe_richtung(dreh: Mapping | None) -> tuple[float, float]:
    """Einheitsvektor, in dem die Tiefe nach hinten läuft: schräg nach rechts unten, bei gedrehtem Objekt (3D-Drehung X/Y) entsprechend verschoben."""
    return eigene_kopie(_fw.tiefe_richtung(dreh))


def dreht(dreh: dict | None) -> bool:
    """Dreht die 3D-Drehung das Bild tatsächlich (ein Winkel ungleich 0)?"""
    return _fw.dreht(dreh)
