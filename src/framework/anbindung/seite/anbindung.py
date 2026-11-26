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


def papier_name(width_mm: float, height_mm: float) -> str:
    """Der Name des Papierformats mit diesen Maßen (hoch oder quer) oder „Benutzerdefiniert“."""
    return _k.PageSettings(width_mm=width_mm, height_mm=height_mm).paper_name()


def inhalt_px(width_mm: float, height_mm: float, margin_top_mm: float, margin_bottom_mm: float, margin_left_mm: float,
              margin_right_mm: float) -> tuple[float, float]:
    """(Breite, Höhe) der Textfläche einer Seite in Bildpunkten; die Höhe im Raster des Seitenumbruchs."""
    s = _k.PageSettings(width_mm=width_mm, height_mm=height_mm, margin_top_mm=margin_top_mm, margin_bottom_mm=margin_bottom_mm,
                        margin_left_mm=margin_left_mm, margin_right_mm=margin_right_mm)
    return s.content_width_px, s.content_height_px
