"""Unveränderliche Vorgaben neuer freier Objekte (Textfeld, WordArt) für die Oberfläche."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextfeldVorgabe:
    """Womit ein neues Textfeld beginnt: Text, Schrift, Schriftgröße in Punkt und Schriftfarbe."""
    text: str
    schrift: str
    pt: int
    farbe: str


@dataclass(frozen=True)
class WordartVorgabe:
    """Womit ein neues WordArt beginnt: Text, Nummer der Formatvorlage, Schriftgröße in Punkt und Schrift."""
    text: str
    vorlage: int
    pt: int
    schrift: str
