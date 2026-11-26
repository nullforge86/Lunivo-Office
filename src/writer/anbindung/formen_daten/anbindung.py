"""Anbindung der Oberfläche an ``core.objekte.formen.formen_daten`` über ``framework.anbindung.formen_daten``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import framework.anbindung.formen_daten as _fw
from writer.werte import eigene_kopie


@cache
def gruppen_abstand():
    return eigene_kopie(_fw.gruppen_abstand())


@cache
def standard():
    return eigene_kopie(_fw.standard())


@cache
def vorlagen():
    return eigene_kopie(_fw.vorlagen())


def form_daten(o: Mapping, breite: float, hoehe: float) -> Mapping:
    return eigene_kopie(_fw.form_daten(o, breite, hoehe))


@cache
def fo_schluessel():
    """Felder der Formbefehle → Schlüssel der Angabe des Objekts."""
    return eigene_kopie(_fw.fo_schluessel())


def muster_an(schluessel: str, x: int, y: int) -> bool:
    """Ist das Bildelement (x, y) der 8 × 8-Kachel des Musters in der Musterfarbe?"""
    return _fw.muster_an(schluessel, x, y)


def form_daten_setzen(d: dict, k: str, v) -> None:
    """Bei einer Form: Farben der Form selbst in die Formdaten ``d`` schreiben, kein Kasten ums Bild."""
    schluessel, wert = _fw.form_daten_setzen(k, v)
    d[schluessel] = wert


def kette_glieder(k, a, nach_id: dict) -> list:
    """Alle Felder einer Kette verknüpfter Textfelder ab ``(k, a)`` in Reihenfolge."""
    return list(_fw.kette_glieder(k, a, nach_id))


def verknuepfbar(felder: dict, von_key: tuple, nach_key: tuple):
    """(Daten von ``von``, Daten von ``nach``) als Kopien mit Kennung, wenn die Verknüpfung erlaubt ist; sonst None."""
    return _fw.verknuepfbar(felder, von_key, nach_key)
