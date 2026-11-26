"""Angaben der Objekte für die Bedienung: ordnet sie den Framework-Befehlen zu; die Oberfläche bekommt eigene Kopien und Ids, keine Objekte des Kerns."""
from __future__ import annotations

from framework.befehle import objekte as _befehle
from writer.werte import eigene_kopie


def objekt_angabe(kennung: int, objekt_id: int) -> dict | None:
    """Die Angabe des frei positionierten Objekts (eigene Kopie); ``None``, wenn es das Objekt nicht gibt."""
    return eigene_kopie(_befehle.objektangaben_angabe(kennung, objekt_id))


def objekt_angabe_speichern(kennung: int, objekt_id: int, angabe: dict, bilder: dict) -> bool:
    """Schreibt die Angabe eines freien Objekts zurück, mit den dafür bereitgelegten Bildern (Name → Daten), in einem Schritt."""
    return _befehle.objektangaben_angabe_speichern(kennung, objekt_id, angabe, bilder)


def inline_gewaehlt(kennung: int) -> int | None:
    """Id des Objekts im Text, das die Auswahl genau umfasst (ein Zeichen), sonst ``None``."""
    return _befehle.objektangaben_inline_gewaehlt(kennung)


def inline_der_auswahl(kennung: int) -> tuple[int, ...] | None:
    """Ids der Objekte im Text, wenn die Auswahl nur aus Objekten (und Leerraum) besteht; sonst ``None``."""
    return _befehle.objektangaben_inline_der_auswahl(kennung)


def inline_an(kennung: int, absatz_id: int, stellen: tuple[int, ...]) -> tuple[int, ...]:
    """Ids der Objekte im Text des Absatzes, die an einer der Zeichenstellen stehen, in Textreihenfolge."""
    return _befehle.objektangaben_inline_an(kennung, absatz_id, tuple(stellen))


def objekt_textfelder(kennung: int) -> list[tuple[tuple, dict]]:
    """Alle freien Textfelder des Dokuments: (Schlüssel, Angabe) in Dokumentreihenfolge, als eigene Kopien."""
    return [(schluessel, eigene_kopie(angabe)) for schluessel, angabe in _befehle.objektangaben_textfelder(kennung)]
