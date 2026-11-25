"""Wasserzeichen: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import wasserzeichen as befehle
from framework.schnittstellen.datentypen.wasserzeichendaten import Wasserzeichenangabe

VORGABEN: tuple[str, ...] = befehle.VORGABEN
GROESSEN: tuple[int, ...] = befehle.GROESSEN
ZOOMS: tuple[int, ...] = befehle.ZOOMS
HORIZONTAL: tuple[tuple[str, str], ...] = befehle.HORIZONTAL
VERTIKAL: tuple[tuple[str, str], ...] = befehle.VERTIKAL
FORMATE: tuple[tuple[int, str], ...] = befehle.FORMATE
STANDARD_FARBE: str = befehle.STANDARD_FARBE


def da(w: Wasserzeichenangabe | None) -> bool:
    return befehle.da(w)
