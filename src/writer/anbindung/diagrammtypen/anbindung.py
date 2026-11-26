"""Anbindung der Oberfläche an ``core.layout.drucklayout.ausgabe.diagramm.diagrammtypen`` über ``framework.anbindung.diagrammtypen``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.diagrammtypen as _fw
from writer.werte import eigene_kopie


@cache
def alt():
    return eigene_kopie(_fw.alt())


@cache
def beispiel_kategorien():
    return eigene_kopie(_fw.beispiel_kategorien())


@cache
def beispiel_reihen():
    return eigene_kopie(_fw.beispiel_reihen())


@cache
def farben():
    return eigene_kopie(_fw.farben())


@cache
def kombi_typen():
    return eigene_kopie(_fw.kombi_typen())


@cache
def namen():
    return eigene_kopie(_fw.namen())


@cache
def typen():
    return eigene_kopie(_fw.typen())


@cache
def vorlagen():
    return eigene_kopie(_fw.vorlagen())


def art(daten: dict) -> str:
    """Der Untertyp des Diagramms (feste Vorlagen und alte Namen aufgelöst)."""
    return _fw.art(daten)


def beispiel(untertyp: str) -> tuple[str, list[str], dict[str, list[float]]]:
    """Beispieldaten für die Vorschau nach Art des Untertyps: (Titel, Rubriken, Reihen)."""
    return eigene_kopie(_fw.beispiel(untertyp))


def hat_linien(u: str) -> bool:
    """Arten mit Linienreihen (Pfeile, Linienformat)."""
    return _fw.hat_linien(u)


def ist_kreis(u: str) -> bool:
    """Alle Kreisarten (Kreis, 3D-Kreis, Kreis/Balken von Kreis, Ring)."""
    return _fw.ist_kreis(u)


def kombi_vorgabe(untertyp: str, anzahl: int) -> list[tuple[str, bool]]:
    """Belegung der Kombinationstabelle für eine fertige Kombination (die letzte Reihe ist Linie bzw. Säule)."""
    return eigene_kopie(_fw.kombi_vorgabe(untertyp, anzahl))
