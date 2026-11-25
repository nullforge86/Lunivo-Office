"""Anbindung an ``core.layout.drucklayout.geometrie``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from functools import cache

import core.layout.drucklayout as _k
from framework.anbindung import fest


@cache
def blatt_abstand_px() -> float:
    return fest(_k.BLATT_ABSTAND_PX)
