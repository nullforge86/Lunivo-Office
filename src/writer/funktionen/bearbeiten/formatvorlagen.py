"""Formatvorlagen: ordnet die Bedienung (Katalog, Band, Tastenkürzel) den Framework-Befehlen zu."""
from __future__ import annotations

from collections.abc import Mapping

from framework.befehle import bearbeiten as _befehle


def formatvorlage_anwenden(kennung: int, name: str) -> bool:
    return _befehle.formatvorlage_anwenden(kennung, name)


def formatvorlage_abgleichen(kennung: int, name: str) -> bool:
    return _befehle.formatvorlage_abgleichen(kennung, name)


def tabs_als_text(stopps: tuple[tuple[float, str, str], ...]) -> str:
    return _befehle.tabs_als_text(tuple(stopps))


def tabs_aus_text(text: str | None) -> tuple[tuple[float, str, str], ...]:
    return _befehle.tabs_aus_text(text)


def formatvorlage_aus_auswahl(kennung: int) -> Mapping[str, str | float | int | bool]:
    return _befehle.formatvorlage_aus_auswahl(kennung)
