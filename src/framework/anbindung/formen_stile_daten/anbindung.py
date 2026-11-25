"""Anbindung an ``core.objekte.formen.formen_stile_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Sequence
from functools import cache

import core.objekte.formen as _k
from framework.anbindung import fest


@cache
def spalten() -> Sequence[tuple[str, str]]:
    return fest(_k.SPALTEN)


@cache
def zeilen() -> Sequence[str]:
    return fest(_k.ZEILEN)
