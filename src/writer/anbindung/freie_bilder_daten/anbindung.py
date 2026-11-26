"""Anbindung der Oberfläche an ``core.objekte.formen.freie_bilder_daten`` über ``framework.anbindung.freie_bilder_daten``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.freie_bilder_daten as _fw
from writer.werte import eigene_kopie


@cache
def max_bildpunkte():
    return eigene_kopie(_fw.max_bildpunkte())


@cache
def schema():
    return eigene_kopie(_fw.schema())


def text_gerade(dreh: float, fx: dict | None) -> bool:
    """„Text nicht drehen“: Form und Füllung gedreht, der Text bleibt aufrecht."""
    return _fw.text_gerade(dreh, fx)


def rechteck(anker: tuple[str, float, str, str, float, str], b: float, h: float, blatt_b: float, blatt_h: float, ml: float, mt: float, inhalt_b: float,
             inhalt_h: float, absatz_y: float = 0.0, spalte_x: float | None = None, seite: int = 1) -> tuple[float, float, float, float]:
    """Das Rechteck eines Objekts auf dem Blatt als ``(x, y, Breite, Höhe)``; ``anker``: (Bezug waagerecht, x, Ausrichtung, Bezug senkrecht, y, Ausrichtung)."""
    return _fw.rechteck(anker, b, h, blatt_b, blatt_h, ml, mt, inhalt_b, inhalt_h, absatz_y, spalte_x, seite)
