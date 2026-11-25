"""Anbindung an ``core.objekte.formen.freie_bilder_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.objekte.formen as _k
from framework.anbindung import fest


@cache
def max_bildpunkte() -> int:
    return fest(_k.MAX_BILDPUNKTE)


@cache
def schema() -> Mapping[str, str]:
    return fest(_k.SCHEMA)
