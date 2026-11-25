"""Bildeffekte: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import bildeffekte as befehle
from framework.schnittstellen.datentypen.effektdaten import EffektDaten

ABSCHLUSS: tuple[tuple[str, str], ...] = befehle.ABSCHLUSS


def vorgabe() -> EffektDaten:
    return befehle.vorgabe()
