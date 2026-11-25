"""Anbindung an ``core.dokument.abschnitte.seite``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.dokument.abschnitte as _k
from framework.anbindung import fest


@cache
def paper_mm() -> Mapping[str, tuple[float, float]]:
    return fest(_k.PAPER_MM)
