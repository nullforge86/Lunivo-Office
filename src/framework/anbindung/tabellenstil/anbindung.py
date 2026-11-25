"""Anbindung an ``core.tabellen.formatierung.tabellenstil``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.tabellen.formatierung as _k
from framework.anbindung import fest


@cache
def vorlagen() -> Mapping[str, tuple[None, None, None, int] | tuple[str, str, str, int]]:
    return fest(_k.VORLAGEN)
