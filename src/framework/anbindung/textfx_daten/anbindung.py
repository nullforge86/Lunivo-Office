"""Anbindung an ``core.objekte.wordart.textfx_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.objekte.wordart as _k
from framework.anbindung import fest


@cache
def warp_formen() -> tuple[tuple[str, str], ...]:
    return fest(_k.WARP_FORMEN)


@cache
def bahnen() -> Mapping[str, tuple[tuple[float, float], ...]]:
    """Bahnen der Mehrfachlinien: (Abstand von der Mitte, Dicke) in Linienbreiten."""
    return fest(_k.BAHNEN)


def tiefe_faktor(mat: str, licht: str, t: float) -> float:
    """Helligkeitsfaktor einer Tiefenschicht ``t`` (0..1) nach Material und Beleuchtung."""
    return _k.tiefe_faktor(mat, licht, t)
