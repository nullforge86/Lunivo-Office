"""Anbindung an ``core.objekte.formen.bildeffekte_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.objekte.formen as _k
from framework.anbindung import fest


@cache
def px_pt() -> float:
    return fest(_k.PX_PT)


def hat_abschluss(fx: Mapping | None) -> bool:
    return fest(_k.hat_abschluss(fx))


def tiefe_richtung(dreh: Mapping | None) -> tuple[float, float]:
    """Einheitsvektor, in dem die Tiefe nach hinten läuft: schräg nach rechts unten, bei gedrehtem Objekt (3D-Drehung X/Y) entsprechend verschoben."""
    return fest(_k.tiefe_richtung(dreh))
