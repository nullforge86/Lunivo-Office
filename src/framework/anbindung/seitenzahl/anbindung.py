"""Anbindung an ``core.dokument.kopf_fusszeilen.seitenzahl``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Sequence
from functools import cache

import core.dokument.kopf_fusszeilen as _k
from framework.anbindung import fest


@cache
def muster() -> Sequence[tuple[str, str, str]]:
    return fest(_k.MUSTER)


@cache
def positionen() -> Sequence[tuple[str, str, str]]:
    return fest(_k.POSITIONEN)


@cache
def trenner() -> Sequence[tuple[str, str, str]]:
    return fest(_k.TRENNER)


@cache
def vorgaben() -> Sequence[tuple[str, str, str, str]]:
    return fest(_k.VORGABEN)
