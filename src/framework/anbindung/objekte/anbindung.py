"""Anbindung an ``core.layout.drucklayout.ausgabe.objekte.objekte``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations


import core.layout.drucklayout.ausgabe.objekte as _k
from framework.anbindung import fest


def dunkler(farbe: tuple[int, int, int, int], faktor: int = 200) -> tuple[int, int, int, int]:
    """Abdunkeln wie ``QColor.darker``: der Hellwert (V) wird mit 100 / ``faktor`` multipliziert."""
    return fest(_k.dunkler(farbe, faktor))


def heller(farbe: tuple[int, int, int, int], faktor: int = 160) -> tuple[int, int, int, int]:
    """Aufhellen wie ``QColor.lighter``: der Hellwert (V) wird mit ``faktor`` / 100 multipliziert; was über 255 hinausgeht, nimmt die Sättigung weg."""
    return fest(_k.heller(farbe, faktor))
