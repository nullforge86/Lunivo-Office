"""Anbindung an ``core.diagramme.daten.diagramm_zusatz``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.diagramme.daten as _k
from framework.anbindung import fest


@cache
def elemente() -> tuple[str, ...]:
    return fest(_k.ELEMENTE)


@cache
def element_namen() -> Mapping[str, str]:
    return fest(_k.ELEMENT_NAMEN)


@cache
def legenden_lagen() -> tuple[str, str, str, str]:
    return fest(_k.LEGENDEN_LAGEN)


@cache
def standard_elemente() -> Mapping[str, bool]:
    return fest(_k.STANDARD_ELEMENTE)


def elemente_wirksam(d: Mapping) -> Mapping:
    """Alle neun Elemente mit ihrem Wert: Wahrheitswerte, bei ``legende`` die Lage (``oben`` … ``rechts``) oder ``aus``."""
    return fest(_k.elemente_wirksam(d))
