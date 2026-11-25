"""Einstellungen der Funktion „Überprüfen“: Darstellung des Markups in Sprechblasen."""
from __future__ import annotations

from core.objekte.formen import sprechblasen_modell as sprechblasen
from framework.schnittstellen.einstellungen import Einstellungen

BALLONS = "sprechblasen/verwenden"
BALLON_WERTE = (("Sprechblasen für Überarbeitungen verwenden", "Immer"), ("Alle Überarbeitungen inline anzeigen", "Nie"),
                ("Nur Kommentare in Sprechblasen anzeigen", "Nur für Kommentare"))


def ballons(e: Einstellungen) -> str:
    return e.get(BALLONS, sprechblasen.STANDARD["verwenden"])


def ballons_setzen(e: Einstellungen, wert: str) -> None:
    e.set(BALLONS, wert)
