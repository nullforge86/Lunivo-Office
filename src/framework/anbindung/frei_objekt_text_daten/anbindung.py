"""Anbindung an ``core.objekte.textfelder.modell.frei_objekt_text_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import core.objekte.textfelder.modell as _k
from framework.anbindung import fest


@cache
def arten() -> tuple[str, ...]:
    return fest(_k.frei_objekt_text_daten_ARTEN)


@cache
def form_standard() -> Mapping[str, float | str]:
    return fest(_k.FORM_STANDARD)


@cache
def standard_mass() -> Mapping[str, tuple[int, int]]:
    return fest(_k.STANDARD_MASS)


@cache
def textfeld_fuell() -> Mapping[str, str]:
    return fest(_k.TEXTFELD_FUELL)


@cache
def textfeld_rand() -> Mapping[str, float | str]:
    return fest(_k.TEXTFELD_RAND)


@cache
def text_arten() -> tuple[str, str]:
    return fest(_k.TEXT_ARTEN)


def laeufe_ab(laeufe: Sequence[Mapping], von: int, bis: int | None = None) -> Sequence[Mapping]:
    """Der Ausschnitt ``[von, bis)`` des Gesamttextes mit seinen Formaten."""
    return fest(_k.laeufe_ab(laeufe, von, bis))


def laeufe_zusammen(laeufe: Sequence[Mapping]) -> Sequence[Mapping]:
    """Benachbarte Läufe mit gleichem Format zu einem verbinden (leere fallen weg)."""
    return fest(_k.laeufe_zusammen(laeufe))


@cache
def ss() -> int:
    """Faktor, in dem Objekte gezeichnet werden (doppelte Auflösung: scharf auch bei Zoom)."""
    return fest(_k.SS)


def gedreht(richtung: str | None) -> bool:
    """Läuft der Text nicht waagerecht?"""
    return _k.gedreht(richtung)
