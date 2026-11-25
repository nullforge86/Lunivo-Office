"""Muster der Schattierung und der Musterfüllung: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import muster as befehle
from writer.werte import unveraenderlich


def muster_vorlagen() -> tuple[tuple[str, str, str], ...]:
    return unveraenderlich(befehle.MUSTER)

def name_von(schluessel: str) -> str:
    return befehle.name_von(schluessel)
