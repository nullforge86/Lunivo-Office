"""Anbindung an ``core.text.statistik``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import core.text as _k
from framework.anbindung import fest


def zaehlen(texte: Sequence[str], seiten: int = 1) -> Mapping:
    """``texte``: ein Eintrag je Absatz (auch Noten und Textfelder, wenn sie mitzählen sollen)."""
    return fest(_k.zaehlen(texte, seiten))
