"""Anbindung an ``core.dokument.felder_text_kern``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations


import core.dokument as _k
from framework.anbindung import fest


def ohne_schalter(anweisung: str) -> str:
    return fest(_k.ohne_schalter(anweisung))
