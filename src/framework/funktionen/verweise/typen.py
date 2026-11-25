"""Eigene, unveränderliche Datentypen der Funktion „Verweise“ für die Oberfläche."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BeschriftungsStart:
    """Ausgangswerte des Fensters „Beschriftung“."""
    eigene: tuple[str, ...]          # eigene Bezeichnungen aus den Einstellungen
    objekt: bool                     # an der Schreibmarke steht eine Tabelle oder ein Objekt
    label: str                       # vorgeschlagene Bezeichnung („Tabelle“ oder „Abbildung“)


@dataclass(frozen=True)
class IndexStart:
    """Ausgangswerte des Fensters „Indexeintrag festlegen“."""
    vorschlag: str
    marken: tuple[str, ...]
    auswahl: bool


@dataclass(frozen=True)
class IndexEintrag:
    """Ein Indexeintrag wie im DOCX-Feld XE (Haupt- und Untereintrag, Lesung, „Siehe …“, Seitenbereich, fett/kursiv)."""
    haupt: str
    unter: str = ""
    lesung: str = ""
    lesung_unter: str = ""
    siehe: str = ""
    marke: str = ""
    fett: bool = False
    kursiv: bool = False
