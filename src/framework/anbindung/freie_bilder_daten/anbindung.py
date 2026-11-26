"""Anbindung an ``core.objekte.formen.freie_bilder_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.objekte.formen as _k
from framework.anbindung import Daten, fest


@cache
def max_bildpunkte() -> int:
    return fest(_k.MAX_BILDPUNKTE)


@cache
def schema() -> Mapping[str, str]:
    return fest(_k.SCHEMA)


def text_gerade(dreh: float, fx: Mapping[str, Daten] | None) -> bool:
    """„Text nicht drehen“: Form und Füllung gedreht, der Text bleibt aufrecht."""
    return _k.text_gerade(dreh, fx)


def rechteck(anker: tuple[str, float, str, str, float, str], b: float, h: float, blatt_b: float, blatt_h: float, ml: float, mt: float, inhalt_b: float,
             inhalt_h: float, absatz_y: float = 0.0, spalte_x: float | None = None, seite: int = 1) -> tuple[float, float, float, float]:
    """Das Rechteck eines Objekts auf dem Blatt als ``(x, y, Breite, Höhe)``; ``anker``: (Bezug waagerecht, x, Ausrichtung, Bezug senkrecht, y, Ausrichtung)."""
    from core.layout.drucklayout import objekte_objekt_rechteck
    from core.objekte.anordnung import Anchor
    r = objekte_objekt_rechteck(Anchor(*anker), b, h, blatt_b, blatt_h, ml, mt, inhalt_b, inhalt_h, absatz_y, spalte_x, seite)
    return r.x, r.y, r.width, r.height
