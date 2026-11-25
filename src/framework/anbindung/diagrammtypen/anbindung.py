"""Anbindung an ``core.layout.drucklayout.ausgabe.diagramm.diagrammtypen``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import core.layout.drucklayout.ausgabe.diagramm as _k
from framework.anbindung import fest


@cache
def alt() -> Mapping[str, str]:
    return fest(_k.ALT)


@cache
def beispiel_kategorien() -> Sequence[str]:
    return fest(_k.BEISPIEL_KATEGORIEN)


@cache
def beispiel_reihen() -> Mapping[str, Sequence[float]]:
    return fest(_k.BEISPIEL_REIHEN)


@cache
def farben() -> Sequence[str]:
    return fest(_k.FARBEN)


@cache
def kombi_typen() -> Sequence[tuple[str, str]]:
    return fest(_k.KOMBI_TYPEN)


@cache
def namen() -> Mapping[str, str]:
    return fest(_k.NAMEN)


@cache
def typen() -> Sequence[tuple[str, str, Sequence[tuple[str, str]]]]:
    return fest(_k.TYPEN)


@cache
def vorlagen() -> Mapping[str, tuple[str, Sequence[str]]]:
    return fest(_k.VORLAGEN)
