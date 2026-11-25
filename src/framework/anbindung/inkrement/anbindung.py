"""Anbindung an ``core.korrektur.inkrement``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations


import core.korrektur as _k
from framework.anbindung import fest


def lohnt(laenge: int, von: int, bis: int) -> bool:
    return fest(_k.lohnt(laenge, von, bis))


def pruefbereich(text: str, a: int, b: int, absaetze: int = 1) -> tuple[int, int]:
    """Den geänderten Bereich auf ganze Absätze samt Sicherheitsbereich erweitern."""
    return fest(_k.pruefbereich(text, a, b, absaetze))


def schmutz_abbilden(bereich: tuple[int, int] | None, pos: int, entfernt: int, hinzu: int) -> tuple[int, int]:
    """Den bisher ungeprüften Bereich in die neuen Positionen umrechnen und um die neue Änderung erweitern."""
    return fest(_k.schmutz_abbilden(bereich, pos, entfernt, hinzu))
