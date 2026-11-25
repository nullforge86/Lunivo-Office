"""Anbindung an ``core.objekte.formen.formen_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import core.objekte.formen as _k
from framework.anbindung import fest


@cache
def gruppen_abstand() -> int:
    return fest(_k.GRUPPEN_ABSTAND)


@cache
def standard() -> Mapping[str, float | str]:
    return fest(_k.formen_daten_STANDARD)


@cache
def vorlagen() -> Sequence[tuple[str, str, str, float]]:
    return fest(_k.VORLAGEN)


def form_daten(o: Mapping, breite: float, hoehe: float) -> Mapping:
    return fest(_k.form_daten(o, breite, hoehe))
