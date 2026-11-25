"""Anbindung an ``core.dokument.zusatz``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from functools import cache

import core.dokument as _k
from framework.anbindung import fest


@cache
def ki_autor() -> str:
    return fest(_k.KI_AUTOR)


def kommentar_farbe(geloest: bool = False) -> str:
    return fest(_k.kommentar_farbe(geloest))


def roemisch(n: int) -> str:
    return fest(_k.roemisch(n))
