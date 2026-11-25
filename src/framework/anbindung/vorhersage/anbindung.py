"""Anbindung an ``core.korrektur.woerterbuecher.vorhersage``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import core.korrektur.woerterbuecher as _k
from framework.anbindung import fest


@cache
def empfaenger() -> Sequence[str]:
    return fest(_k.EMPFAENGER)


def faengt_an_mit(anfang: str, hoechstens: int = 8, gelernt: Mapping | None = None, thema: frozenset = frozenset()) -> Sequence[str]:
    return fest(_k.faengt_an_mit(anfang, hoechstens, gelernt, thema))


def thema_woerter(name: str) -> frozenset:
    return fest(_k.thema_woerter(name))
