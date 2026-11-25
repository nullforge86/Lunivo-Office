"""Anbindung an ``core.objekte.formen.linie_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from functools import cache

import core.objekte.formen as _k
from framework.anbindung import fest


@cache
def alle_seiten() -> str:
    return fest(_k.ALLE_SEITEN)


@cache
def linienbreiten() -> tuple[float, ...]:
    return fest(_k.LINIENBREITEN)


@cache
def objekt_striche() -> tuple[tuple[str, str], ...]:
    return fest(_k.OBJEKT_STRICHE)
