"""Anbindung an ``core.listen.aufzaehlungen.listen``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.listen.aufzaehlungen as _k
from framework.anbindung import fest


@cache
def nummerierungen() -> tuple[tuple[str, str, str], ...]:
    return fest(_k.NUMMERIERUNGEN)


@cache
def stile() -> Mapping[str, tuple[str, bool, str, str]]:
    return fest(_k.STILE)


def liste(stil: str, praefix: str = '', suffix: str = '.', start: int = 1, zeichen: Mapping | None = None, pos: Mapping | None = None) -> Mapping:
    """``pos``: eigene Position der Nummer (``ausr``, ``ausr_art``, ``tab``, ``einzug`` in mm) — dann zeichnet Lunivo die Nummer selbst."""
    return fest(_k.liste(stil, praefix, suffix, start, zeichen, pos))


def marke(spec: Mapping) -> str | None:
    """Zeichenfolge für ``liste_zeichner`` (Vorschaubild) dieser Liste."""
    return fest(_k.marke(spec))


def zeichen_filtern(w: Mapping | None) -> Mapping:
    """Aus den Werten eines Schriftart-Fensters nur das, was für Nummern gilt und gesetzt ist."""
    return fest(_k.zeichen_filtern(w))
