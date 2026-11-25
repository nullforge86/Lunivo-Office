"""Vorschläge für ein unbekanntes Wort (Wörterbuch und Klang). Gesucht wird im Kern; die Oberfläche erhält eine unveränderliche Folge."""
from __future__ import annotations

from core.korrektur.sprache import klang


def vorschlaege_fuer(wort: str, hoechstens: int = 6, eigenes: str = "") -> tuple[str, ...]:
    """Bis zu ``hoechstens`` Vorschläge für ``wort``; ``eigenes``: das selbst gelernte Wort zu dieser Schreibweise (leer: keines), es steht dann vorn."""
    gelernt = {"woerter": {str(wort).lower(): eigenes}} if eigenes else None
    return tuple(klang.vorschlaege_fuer(wort, hoechstens, gelernt))
