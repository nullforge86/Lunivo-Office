"""Anbindung an ``core.korrektur.rechtschreibung.autokorrektur``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.korrektur.rechtschreibung as _k
from framework.anbindung import fest


@cache
def schalter() -> Mapping[str, tuple[bool, str]]:
    return fest(_k.SCHALTER)
