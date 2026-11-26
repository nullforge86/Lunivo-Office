"""Anbindung an ``core.layout.drucklayout.ausgabe.diagramm.diagrammtypen``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import core.layout.drucklayout.ausgabe.diagramm as _k
from framework.anbindung import Daten, fest


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


def art(daten: Mapping[str, Daten]) -> str:
    """Der Untertyp des Diagramms (feste Vorlagen und alte Namen aufgelöst)."""
    return _k.art(daten)


def beispiel(untertyp: str) -> tuple[str, Sequence[str], Mapping[str, Sequence[float]]]:
    """Beispieldaten für die Vorschau nach Art des Untertyps: (Titel, Rubriken, Reihen)."""
    return fest(_k.beispiel(untertyp))


def hat_linien(u: str) -> bool:
    """Arten mit Linienreihen (Pfeile, Linienformat)."""
    return _k.hat_linien(u)


def ist_kreis(u: str) -> bool:
    """Alle Kreisarten (Kreis, 3D-Kreis, Kreis/Balken von Kreis, Ring)."""
    return _k.ist_kreis(u)


def kombi_vorgabe(untertyp: str, anzahl: int) -> Sequence[tuple[str, bool]]:
    """Belegung der Kombinationstabelle für eine fertige Kombination (die letzte Reihe ist Linie bzw. Säule)."""
    return fest(_k.kombi_vorgabe(untertyp, anzahl))
