"""Anbindung an ``core.tabellen.modell.tabelle_text``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Sequence
from functools import cache

import core.tabellen.modell as _k
from framework.anbindung import fest


@cache
def trenner() -> Sequence[tuple[str, str]]:
    return fest(_k.TRENNER)


def zellen(texte: Sequence[str], trenner: str) -> Sequence[Sequence[str]]:
    """Absätze in Zeilen und Zellen teilen. Bei „Absatzmarken“ wird jeder Absatz eine Zeile mit einer Zelle."""
    return fest(_k.zellen(texte, trenner))
