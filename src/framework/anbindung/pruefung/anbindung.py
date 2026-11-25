"""Anbindung an ``core.korrektur.rechtschreibung.pruefung``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Sequence
from functools import cache

import core.korrektur.rechtschreibung as _k
from framework.anbindung import fest


@cache
def pruefer_namen() -> Sequence[str]:
    return fest(_k.PRUEFER_NAMEN)
