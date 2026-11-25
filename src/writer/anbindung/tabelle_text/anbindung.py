"""Anbindung der Oberfläche an ``core.tabellen.modell.tabelle_text`` über ``framework.anbindung.tabelle_text``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Sequence
from functools import cache

import framework.anbindung.tabelle_text as _fw
from writer.werte import eigene_kopie


@cache
def trenner():
    return eigene_kopie(_fw.trenner())


def zellen(texte: Sequence[str], trenner: str) -> Sequence[Sequence[str]]:
    """Absätze in Zeilen und Zellen teilen. Bei „Absatzmarken“ wird jeder Absatz eine Zeile mit einer Zelle."""
    return eigene_kopie(_fw.zellen(texte, trenner))
