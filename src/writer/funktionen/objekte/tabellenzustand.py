"""Tabellenzustand an der Schreibmarke: reicht die Abfrage der Minileiste an das Framework weiter."""
from __future__ import annotations

from framework.befehle.objekte import TABELLE_GEWAEHLT as _GEWAEHLT
from framework.befehle.objekte import tabellen_zustand as _zustand, tabellenmodus as _modus

TABELLE_GEWAEHLT: tuple[str, ...] = _GEWAEHLT


def tabellen_zustand(kennung: int) -> str:
    return _zustand(kennung)


def tabellenmodus(kennung: int, rechtsklick: bool = False, per_griff: bool = False) -> bool:
    return _modus(kennung, rechtsklick, per_griff)
