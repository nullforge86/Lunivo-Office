"""Menüs als Daten: Das Framework beschreibt, was ein Menü anbietet; die Oberfläche baut daraus ihr Menü. Unveränderlich und Qt-frei."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Menueeintrag:
    text: str = ""
    symbol: str = ""
    befehl: str = ""                                  # Name des Befehls, den die Oberfläche über writer auslöst
    unter: tuple["Menueeintrag", ...] = ()            # Untermenü
    trenner: bool = False
