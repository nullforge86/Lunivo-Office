"""Deckblätter: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import deckblatt as befehle

NAMEN: tuple[str, ...] = befehle.NAMEN


def deckblatt_entfernen(kennung: int) -> bool:
    return befehle.entfernen(kennung)
