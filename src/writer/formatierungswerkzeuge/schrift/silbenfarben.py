"""Silbenfarben: die Steuerung der Oberfläche. Reicht Abfragen und Befehle an das Framework weiter; die Oberfläche kennt weder Kern noch Speicher."""
from __future__ import annotations

from framework.befehle.ansicht import silbenfarben as befehle
from framework.schnittstellen.einstellungen import Einstellungen
from framework.schnittstellen.silbenfarben import SilbenEinstellung, SilbenKatalog


def katalog() -> SilbenKatalog:
    return befehle.katalog()


def einstellung_lesen(e: Einstellungen) -> SilbenEinstellung:
    return befehle.einstellung_lesen(e)


def einstellung_speichern(e: Einstellungen, k: SilbenEinstellung) -> None:
    befehle.einstellung_speichern(e, k)


def neue_einstellung(**felder: object) -> SilbenEinstellung:
    return befehle.neue_einstellung(**felder)


def farben(k: SilbenEinstellung) -> tuple[str, ...]:
    return befehle.farben(k)


def silben(wort: str, sprache: str = "de_DE") -> tuple[str, ...]:
    return befehle.silben(wort, sprache)


def fuer_den_druck(k: SilbenEinstellung) -> SilbenEinstellung | None:
    return befehle.fuer_den_druck(k)
