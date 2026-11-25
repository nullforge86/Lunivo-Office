"""Format der Diagrammteile und Textfelder: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import diagrammformat as befehle
from writer.werte import unveraenderlich


def diagramm_vertikal_ausrichtungen() -> tuple[tuple[str, str], ...]:
    return unveraenderlich(befehle.VERTIKAL)


def diagramm_strichtypen() -> tuple[tuple[str, str], ...]:
    return unveraenderlich(befehle.STRICHTYPEN)


def diagramm_pfeile() -> tuple[tuple[str, str], ...]:
    return unveraenderlich(befehle.PFEILE)


def diagramm_pfeil_groessen() -> tuple[tuple[float, str], ...]:
    return unveraenderlich(befehle.PFEIL_GROESSEN)

def strich_schluessel(art: str | None) -> str:
    return befehle.strich_schluessel(art)
