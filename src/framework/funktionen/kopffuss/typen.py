"""Eigene, unveränderliche Datentypen der Funktion „Kopf- und Fußzeile“ für die Oberfläche."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KopfFussOptionen:
    erste_seite_anders: bool
    gerade_ungerade: bool
    kopf_abstand_mm: float
    fuss_abstand_mm: float


@dataclass(frozen=True)
class MenueEintrag:
    """Ein Eintrag einer Klappe als Daten: ``aktion`` ist ein Name für ``KopfFussBefehle.ausfuehren``; ohne ``text`` ist es ein Trenner."""
    text: str = ""
    aktion: str = ""
    aktiv: bool = True

    @property
    def ist_trenner(self) -> bool:
        return not self.text


TRENNER = MenueEintrag()
