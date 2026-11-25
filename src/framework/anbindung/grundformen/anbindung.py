"""Anbindung an ``core.geometrie.grundformen``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from functools import cache

import core.geometrie as _k
from framework.anbindung import fest


@cache
def formen() -> tuple[str, ...]:
    return fest(_k.GRUNDFORMEN)
