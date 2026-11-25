"""Fläche und Rasterbild: Die Oberfläche beschreibt, wo und wie fein gezeichnet wird; der Kern zeichnet auf seine eigene Zeichenfläche."""
from __future__ import annotations

from typing import NamedTuple


class Flaeche(NamedTuple):
    """Die Zeichenfläche: Größe in Bildpunkten (96 dpi), Auflösungsfaktor, Ursprung (links oben, in Koordinaten des Inhalts) und Papierfarbe RGBA."""
    breite: float
    hoehe: float
    faktor: float = 1.0
    x: float = 0.0
    y: float = 0.0
    grund: tuple[int, int, int, int] = (255, 255, 255, 0)


class Rasterbild(NamedTuple):
    """Fertige Bildpunkte: Breite und Höhe in Pixeln, Daten als RGBA (8 Bit je Kanal, Zeile für Zeile)."""
    breite: int
    hoehe: int
    daten: bytes


class Rechteck(NamedTuple):
    """Ein Rechteck in Bildpunkten: links, oben, Breite, Höhe."""
    x: float
    y: float
    breite: float
    hoehe: float


def _malen(flaeche: Flaeche, zeichne) -> Rasterbild:
    from core.geometrie import Point
    from core.layout.drucklayout.ausgabe import RasterZiel
    from framework.dokumentverwaltung.ausgabe import standard_engine
    b, h, faktor, x, y, grund = flaeche
    ziel = RasterZiel(standard_engine(), b, h, faktor, tuple(grund))
    if x or y:
        ziel.push_state(translate=Point(-x, -y))
    zeichne(ziel)
    b, h, roh = ziel.als_rgba()
    return Rasterbild(b, h, bytes(roh))


def _rect(r: Rechteck):
    from core.geometrie import Rect
    return Rect(float(r[0]), float(r[1]), float(r[2]), float(r[3]))
