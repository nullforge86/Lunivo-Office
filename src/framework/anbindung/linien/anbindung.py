"""Anbindung an ``core.layout.drucklayout.ausgabe.objekte.linien``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import core.layout.drucklayout.ausgabe.objekte as _k
from framework.anbindung import fest


@cache
def stile() -> Mapping[str, tuple[None | Sequence[tuple[float, float] | tuple[int, float]] | bool | str, ...] | tuple[None | Sequence[tuple[float, float]] | bool | str, ...] | tuple[None | Sequence[tuple[int, float]] | bool | str, ...] | tuple[Sequence[tuple[int, float]] | bool | str | tuple[float, float], ...] | tuple[Sequence[tuple[int, float]] | bool | str, ...]]:
    return fest(_k.STILE)
