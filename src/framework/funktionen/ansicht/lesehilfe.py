"""Lesehilfe: farbige Silben. Liest und ändert den Schalter in den Einstellungen; die Farben selbst berechnet der Programmkern."""
from __future__ import annotations

from core.editor.text import silbenfarben
from framework.schnittstellen.einstellungen import Einstellungen

SILBEN_AN = "lesehilfe/silben/an"


def silben_an(e: Einstellungen) -> bool:
    return bool(silbenfarben.konfig_lesen(e)["an"])


def silben_umschalten(e: Einstellungen) -> bool:
    """Schaltet die Silbenfarben um und gibt den neuen Zustand zurück."""
    neu = not silben_an(e)
    e.set(SILBEN_AN, neu)
    return neu
