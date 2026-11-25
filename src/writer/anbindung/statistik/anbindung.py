"""Anbindung der Oberfläche an ``core.text.statistik`` über ``framework.anbindung.statistik``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import framework.anbindung.statistik as _fw
from writer.werte import eigene_kopie


def zaehlen(texte: Sequence[str], seiten: int = 1) -> Mapping:
    """``texte``: ein Eintrag je Absatz (auch Noten und Textfelder, wenn sie mitzählen sollen)."""
    return eigene_kopie(_fw.zaehlen(texte, seiten))
