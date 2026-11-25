"""Verteiler: ordnet den Namen eines Befehls seiner Ausführung zu. Jede Funktion (``framework/funktionen/<name>/befehle.py``) meldet ihre Befehle an."""
from __future__ import annotations

from collections.abc import Callable

from lunivo_writer.farmwork.pruefung import ausgangspruefung as ausgang
from lunivo_writer.farmwork.datentypen.befehlsdaten import Befehl, Ergebnis

Ausfuehrung = Callable[[Befehl], Ergebnis]


class Verteiler:
    def __init__(self) -> None:
        self._ausfuehrungen: dict[str, Ausfuehrung] = {}

    def anmelden(self, name: str, ausfuehrung: Ausfuehrung) -> None:
        if name in self._ausfuehrungen:
            raise ValueError(f"Befehl {name!r} ist bereits angemeldet")
        self._ausfuehrungen[name] = ausfuehrung

    def ausfuehren(self, befehl: Befehl) -> Ergebnis:
        if befehl.name not in self._ausfuehrungen:
            return Ergebnis(ok=False, text=f"Unbekannter Befehl: {befehl.name}")
        return ausgang.pruefe(self._ausfuehrungen[befehl.name](befehl), f"Ergebnis von {befehl.name}")


verteiler = Verteiler()
