"""Anbindung an ``core.text.zahlformat``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Sequence
from functools import cache

import core.text as _k
from framework.anbindung import fest


@cache
def typen() -> Sequence[tuple[str, str]]:
    return fest(_k.TYPEN)


def zahl_text(n: int, typ: str) -> str:
    """Die Zahl im gewählten Typ; liegt sie außerhalb der Grenzen, ``ValueError``."""
    return fest(_k.zahl_text(n, typ))
