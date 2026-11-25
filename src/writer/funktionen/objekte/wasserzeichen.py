"""Wasserzeichen: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import wasserzeichen as befehle
from framework.schnittstellen.datentypen.wasserzeichendaten import Wasserzeichenangabe
from writer.werte import unveraenderlich


def wasserzeichen_vorgaben() -> tuple[str, ...]:
    return unveraenderlich(befehle.VORGABEN)


def wasserzeichen_groessen() -> tuple[int, ...]:
    return unveraenderlich(befehle.GROESSEN)


def wasserzeichen_zooms() -> tuple[int, ...]:
    return unveraenderlich(befehle.ZOOMS)


def wasserzeichen_horizontal() -> tuple[tuple[str, str], ...]:
    return unveraenderlich(befehle.HORIZONTAL)


def wasserzeichen_vertikal() -> tuple[tuple[str, str], ...]:
    return unveraenderlich(befehle.VERTIKAL)


def wasserzeichen_formate() -> tuple[tuple[int, str], ...]:
    return unveraenderlich(befehle.FORMATE)


def wasserzeichen_standard_farbe() -> str:
    return str(befehle.STANDARD_FARBE)

def da(w: Wasserzeichenangabe | None) -> bool:
    return befehle.da(w)
