"""Anbindung an ``core.listen.listen``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.listen as _k
from framework.anbindung import fest


@cache
def platzhalter() -> str:
    return fest(_k.PLATZHALTER)


@cache
def zeichen_der_aufzaehlung() -> Mapping[str, str]:
    return fest(_k.ZEICHEN_DER_AUFZAEHLUNG)
