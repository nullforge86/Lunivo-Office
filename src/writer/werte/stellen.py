"""Textstelle und Bereich der Oberfläche: eigene Werte (Absatz-Id und Zeichenstelle), keine Objekte des Kerns."""
from __future__ import annotations

from typing import NamedTuple


class Stelle(NamedTuple):
    absatz_id: int
    versatz: int = 0


class Bereich(NamedTuple):
    anker: Stelle
    kopf: Stelle

    @property
    def leer(self) -> bool:
        return self.anker == self.kopf
