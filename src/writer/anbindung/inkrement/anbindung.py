"""Anbindung der Oberfläche an ``core.korrektur.inkrement`` über ``framework.anbindung.inkrement``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations


import framework.anbindung.inkrement as _fw
from writer.werte import eigene_kopie


def lohnt(laenge: int, von: int, bis: int) -> bool:
    return eigene_kopie(_fw.lohnt(laenge, von, bis))


def pruefbereich(text: str, a: int, b: int, absaetze: int = 1) -> tuple[int, int]:
    """Den geänderten Bereich auf ganze Absätze samt Sicherheitsbereich erweitern."""
    return eigene_kopie(_fw.pruefbereich(text, a, b, absaetze))


def schmutz_abbilden(bereich: tuple[int, int] | None, pos: int, entfernt: int, hinzu: int) -> tuple[int, int]:
    """Den bisher ungeprüften Bereich in die neuen Positionen umrechnen und um die neue Änderung erweitern."""
    return eigene_kopie(_fw.schmutz_abbilden(bereich, pos, entfernt, hinzu))
