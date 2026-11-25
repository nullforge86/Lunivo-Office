"""Anbindung an ``core.dokument.dokument``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from functools import cache

import core.dokument as _k
from framework.anbindung import fest


@cache
def aufzaehlungen() -> tuple[str, str, str, str]:
    return fest(_k.AUFZAEHLUNGEN)


@cache
def listen_ebenen() -> int:
    return fest(_k.LISTEN_EBENEN)
