"""Anbindung an ``core.dokument.abschnitte.seite``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache

import core.dokument.abschnitte as _k
from framework.anbindung import fest


@cache
def paper_mm() -> Mapping[str, tuple[float, float]]:
    return fest(_k.PAPER_MM)


@dataclass(frozen=True)
class Seitenmasse:
    """Blattgröße und Ränder einer Seiteneinrichtung in mm."""
    width_mm: float
    height_mm: float
    margin_top_mm: float
    margin_bottom_mm: float
    margin_left_mm: float
    margin_right_mm: float


@cache
def standardmasse() -> Seitenmasse:
    """Blattgröße und Ränder der Seiteneinrichtung eines neuen Dokuments."""
    s = _k.PageSettings()
    return Seitenmasse(s.width_mm, s.height_mm, s.margin_top_mm, s.margin_bottom_mm, s.margin_left_mm, s.margin_right_mm)
