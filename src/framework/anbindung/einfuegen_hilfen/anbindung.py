"""Anbindung an ``core.bearbeitung.einfuegen_hilfen``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Sequence
from functools import cache

import core.bearbeitung as _k
from framework.anbindung import fest


@cache
def wordart_vorlagen() -> Sequence[tuple[None | float | str, ...] | tuple[None | int | str, ...] | tuple[float | str, ...]]:
    return fest(_k.WORDART_VORLAGEN)
