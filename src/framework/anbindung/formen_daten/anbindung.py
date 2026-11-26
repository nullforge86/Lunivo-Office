"""Anbindung an ``core.objekte.formen.formen_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import core.objekte.formen as _k
from framework.anbindung import fest


@cache
def gruppen_abstand() -> int:
    return fest(_k.GRUPPEN_ABSTAND)


@cache
def standard() -> Mapping[str, float | str]:
    return fest(_k.formen_daten_STANDARD)


@cache
def vorlagen() -> Sequence[tuple[str, str, str, float]]:
    return fest(_k.VORLAGEN)


def form_daten(o: Mapping, breite: float, hoehe: float) -> Mapping:
    return fest(_k.form_daten(o, breite, hoehe))


@cache
def fo_schluessel() -> Mapping[str, str]:
    """Felder der Formbefehle → Schlüssel der Angabe des Objekts."""
    return fest(_k.FO_SCHLUESSEL)


def muster_an(schluessel: str, x: int, y: int) -> bool:
    """Ist das Bildelement (x, y) der 8 × 8-Kachel des Musters in der Musterfarbe?"""
    return _k.muster_an(schluessel, x, y)


def form_daten_setzen(k: str, v: str | float | None) -> tuple[str, str | float]:
    """Bei einer Form: welcher Schlüssel der Formdaten mit welchem Wert zu setzen ist (Farben der Form selbst, kein Kasten ums Bild)."""
    d: dict = {}
    _k.form_daten_setzen(d, k, v)
    return next(iter(d.items()))


def kette_glieder(k: tuple, a: Mapping, nach_id: Mapping) -> Sequence[tuple]:
    """Alle Felder einer Kette verknüpfter Textfelder ab ``(k, a)`` in Reihenfolge (dieselben Einträge, keine Kopien)."""
    return _k.kette_glieder(k, a, nach_id)


def verknuepfbar(felder: Mapping, von_key: tuple, nach_key: tuple) -> tuple[Mapping, Mapping] | None:
    """(Daten von ``von``, Daten von ``nach``) als Kopien mit Kennung, wenn die Verknüpfung erlaubt ist; sonst None."""
    return _k.verknuepfbar(felder, von_key, nach_key)
