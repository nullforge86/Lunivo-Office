"""Vorschläge für ein unbekanntes Wort: die Steuerung der Oberfläche. Reicht die Abfrage an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.korrektur import vorschlaege as befehle


def vorschlaege_fuer(wort: str, hoechstens: int = 6, eigenes: str = "") -> tuple[str, ...]:
    return befehle.vorschlaege_fuer(wort, hoechstens, eigenes)
