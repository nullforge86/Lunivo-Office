"""Anbindung an ``core.objekte.wordart.textfx_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from functools import cache

import core.objekte.wordart as _k
from framework.anbindung import fest


@cache
def warp_formen() -> tuple[tuple[str, str], ...]:
    return fest(_k.WARP_FORMEN)
