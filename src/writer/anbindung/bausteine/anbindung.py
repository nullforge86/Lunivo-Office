"""Textbausteine (AutoText) für die Oberfläche: Listen als eigene Kopien, Merken und Einfügen über das Framework anhand der Kennung."""
from __future__ import annotations

from framework.befehle import bearbeiten as _fw
from writer.werte import eigene_kopie


def laden() -> list[dict]:
    """Die eigenen Textbausteine."""
    return eigene_kopie(_fw.bausteine_eigene())


def standard() -> list[dict]:
    """Die mitgelieferten Textbausteine."""
    return eigene_kopie(_fw.bausteine_standard())


def finde_kuerzel(kuerzel: str) -> dict | None:
    return eigene_kopie(_fw.baustein_fuer_kuerzel(kuerzel))


def hinzufuegen(kennung: int, name: str, kuerzel: str = "") -> None:
    """Die Auswahl des Dokuments ``kennung`` als eigenen Baustein ``name`` speichern."""
    _fw.baustein_merken(kennung, name, kuerzel)


def entfernen(name: str) -> None:
    _fw.baustein_entfernen(name)


def einfuegen(kennung: int, baustein: dict) -> bool:
    """Fügt den Baustein an der Schreibmarke des Dokuments ``kennung`` ein; ``False``, wenn der Kern ablehnt."""
    return _fw.baustein_einfuegen(kennung, baustein)
