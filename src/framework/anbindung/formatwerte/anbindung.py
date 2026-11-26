"""Anbindung an ``core.layout.drucklayout.formatwerte``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.layout.drucklayout as _k
from framework.anbindung import fest


@cache
def standard_familie() -> str:
    return fest(_k.STANDARD_FAMILIE)


def abstaende(a: Mapping) -> tuple[float, float]:
    return fest(_k.abstaende(a))


def einzuege(a: Mapping) -> tuple[float, float, float]:
    """(links, rechts, erste Zeile zusätzlich)."""
    return fest(_k.einzuege(a))


def richtung(a: Mapping) -> str | None:
    """„rtl“ oder „ltr“, wenn der Absatz die Schreibrichtung festlegt; sonst ``None`` (das erste starke Zeichen entscheidet)."""
    return fest(_k.richtung(a))


def tabfuellung(a: Mapping) -> Mapping[float, str]:
    """Position (Bildpunkte) → Füllzeichen der Tabstopps („Position:Schlüssel;…“)."""
    return fest(_k.tabfuellung(a))


def zeilenabstand(a: Mapping) -> tuple[str, float]:
    return fest(_k.zeilenabstand(a))


def schrift(z: Mapping) -> tuple[str, float, int, bool]:
    """Die Schrift eines Textstücks aus dem wirksamen Zeichenformat: (Familie, Größe in pt, Gewicht, kursiv)."""
    f = _k.schrift(z)
    return f.family, f.size_pt, f.weight, f.italic


def tabstopps(a: Mapping) -> tuple[tuple[float, int, str], ...]:
    """((Position, Art, Trennzeichen), …) der Tabstopps des Absatzformats, aufsteigend."""
    from types import SimpleNamespace
    return fest(_k.tabstopps(a, SimpleNamespace(eigenschaften={}))[0])
