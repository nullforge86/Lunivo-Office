"""Format der Diagrammteile und Textfelder: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import diagrammformat as befehle

VERTIKAL: tuple[tuple[str, str], ...] = befehle.VERTIKAL
STRICHTYPEN: tuple[tuple[str, str], ...] = befehle.STRICHTYPEN
PFEILE: tuple[tuple[str, str], ...] = befehle.PFEILE
PFEIL_GROESSEN: tuple[tuple[float, str], ...] = befehle.PFEIL_GROESSEN


def strich_schluessel(art: str | None) -> str:
    return befehle.strich_schluessel(art)
