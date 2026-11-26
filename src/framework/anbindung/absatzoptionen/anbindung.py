"""Anbindung an ``core.formatierung.absatz.absatzoptionen``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.formatierung.absatz as _k
from framework.anbindung import fest


@cache
def vorgabe() -> Mapping[str, bool | str]:
    return fest(_k.VORGABE)


def aus_text(text: str) -> Mapping[str, bool | str]:
    """Die Absatzoptionen aus ihrer Textform (leerer Text: keine)."""
    return fest(_k.aus_text(text))


def als_text(optionen: Mapping[str, bool | str]) -> str:
    """Die Absatzoptionen als Text für das Absatzformat (leer, wenn alle der Vorgabe entsprechen)."""
    return _k.als_text(dict(optionen))
