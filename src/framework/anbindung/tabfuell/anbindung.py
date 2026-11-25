"""Anbindung an ``core.formatierung.absatz.tabfuell``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.formatierung.absatz as _k
from framework.anbindung import fest


@cache
def fuell() -> Mapping[str, tuple[str, str, str]]:
    return fest(_k.FUELL)
