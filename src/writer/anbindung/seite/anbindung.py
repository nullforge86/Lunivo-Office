"""Anbindung der Oberfläche an ``core.dokument.abschnitte.seite`` über ``framework.anbindung.seite``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.seite as _fw
from writer.werte import eigene_kopie


@cache
def paper_mm():
    return eigene_kopie(_fw.paper_mm())


def standardmasse() -> _fw.Seitenmasse:
    """Blattgröße und Ränder (mm) der Seiteneinrichtung eines neuen Dokuments."""
    return _fw.standardmasse()


def papier_name(width_mm: float, height_mm: float) -> str:
    """Der Name des Papierformats mit diesen Maßen (hoch oder quer) oder „Benutzerdefiniert“."""
    return _fw.papier_name(width_mm, height_mm)


def inhalt_px(width_mm: float, height_mm: float, margin_top_mm: float, margin_bottom_mm: float, margin_left_mm: float,
              margin_right_mm: float) -> tuple[float, float]:
    """(Breite, Höhe) der Textfläche einer Seite in Bildpunkten."""
    return _fw.inhalt_px(width_mm, height_mm, margin_top_mm, margin_bottom_mm, margin_left_mm, margin_right_mm)
