"""Anbindung der Oberfläche an ``core.layout.drucklayout.formatwerte`` über ``framework.anbindung.formatwerte``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache
from typing import NamedTuple

import framework.anbindung.formatwerte as _fw
from writer.werte import eigene_kopie


@cache
def standard_familie():
    return eigene_kopie(_fw.standard_familie())


def abstaende(a: Mapping) -> tuple[float, float]:
    return eigene_kopie(_fw.abstaende(a))


def einzuege(a: Mapping) -> tuple[float, float, float]:
    """(links, rechts, erste Zeile zusätzlich)."""
    return eigene_kopie(_fw.einzuege(a))


def richtung(a: Mapping) -> str | None:
    """„rtl“ oder „ltr“, wenn der Absatz die Schreibrichtung festlegt; sonst ``None`` (das erste starke Zeichen entscheidet)."""
    return eigene_kopie(_fw.richtung(a))


def tabfuellung(a: Mapping) -> Mapping[float, str]:
    """Position (Bildpunkte) → Füllzeichen der Tabstopps („Position:Schlüssel;…“)."""
    return eigene_kopie(_fw.tabfuellung(a))


def zeilenabstand(a: Mapping) -> tuple[str, float]:
    return eigene_kopie(_fw.zeilenabstand(a))


class Schriftangabe(NamedTuple):
    """Eine Schrift: Familie, Größe in Punkt, Gewicht (400 normal, 700 fett) und Kursiv."""
    family: str
    size_pt: float
    weight: int = 400
    italic: bool = False


def schrift(z: Mapping) -> Schriftangabe:
    """Die Schrift eines Textstücks aus dem wirksamen Zeichenformat."""
    return Schriftangabe(*_fw.schrift(z))


def tabstopps(a: Mapping) -> tuple[tuple[float, int, str], ...]:
    """((Position, Art, Trennzeichen), …) der Tabstopps des Absatzformats, aufsteigend."""
    return eigene_kopie(_fw.tabstopps(a))
