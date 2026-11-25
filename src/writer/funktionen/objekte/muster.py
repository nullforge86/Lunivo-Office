"""Muster der Schattierung und der Musterfüllung: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import muster as befehle

MUSTER: tuple[tuple[str, str, str], ...] = befehle.MUSTER


def name_von(schluessel: str) -> str:
    return befehle.name_von(schluessel)
