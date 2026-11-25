"""Anbindung der Oberfläche an ``core.layout.drucklayout.ausgabe.objekte.objekte`` über ``framework.anbindung.objekte``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations


import framework.anbindung.objekte as _fw
from writer.werte import eigene_kopie


def dunkler(farbe: tuple[int, int, int, int], faktor: int = 200) -> tuple[int, int, int, int]:
    """Abdunkeln wie ``QColor.darker``: der Hellwert (V) wird mit 100 / ``faktor`` multipliziert."""
    return eigene_kopie(_fw.dunkler(farbe, faktor))


def heller(farbe: tuple[int, int, int, int], faktor: int = 160) -> tuple[int, int, int, int]:
    """Aufhellen wie ``QColor.lighter``: der Hellwert (V) wird mit ``faktor`` / 100 multipliziert; was über 255 hinausgeht, nimmt die Sättigung weg."""
    return eigene_kopie(_fw.heller(farbe, faktor))
