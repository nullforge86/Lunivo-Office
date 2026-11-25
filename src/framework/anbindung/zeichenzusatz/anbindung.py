"""Anbindung an ``core.formatierung.schrift.zeichenzusatz``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from functools import cache

import core.formatierung.schrift as _k
from framework.anbindung import fest


@cache
def ausrichtungen() -> tuple[tuple[str, str], tuple[str, str], tuple[str, str], tuple[str, str]]:
    return fest(_k.ZUSATZ_AUSRICHTUNGEN)


@cache
def formen() -> tuple[tuple[str, str], tuple[str, str], tuple[str, str], tuple[str, str]]:
    return fest(_k.ZUSATZ_FORMEN)


@cache
def vorlagen() -> tuple[tuple[str, str], tuple[str, str], tuple[str, str]]:
    return fest(_k.ZUSATZ_VORLAGEN)


def ruby_text(ruby: str, ausrichtung: str = 'zentriert', abstand: float = 0.0, groesse: float = 7.0) -> str:
    return fest(_k.ruby_text(ruby, ausrichtung, abstand, groesse))


def umschlossen_text(form: str, vorlage: str) -> str:
    return fest(_k.umschlossen_text(form, vorlage))
