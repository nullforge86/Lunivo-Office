"""Anbindung an ``core.suche.textsuche.suche``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from functools import cache

import core.suche.textsuche as _k
from framework.anbindung import fest


@cache
def spezial() -> tuple[tuple[str, str], ...]:
    return fest(_k.SPEZIAL)


@cache
def spezial_ersetzen() -> tuple[tuple[str, str], ...]:
    return fest(_k.SPEZIAL_ERSETZEN)
