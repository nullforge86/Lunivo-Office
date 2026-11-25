"""Melder: Die Oberfläche abonniert Ereignisse ausschließlich hier; das Framework meldet sie. Rückrufe sind einfache Python-Funktionen."""
from __future__ import annotations

from collections.abc import Callable

from lunivo_writer.farmwork.pruefung import ausgangspruefung as ausgang
from lunivo_writer.farmwork.datentypen.ereignisdaten import Art, Ereignis


class Melder:
    def __init__(self) -> None:
        self._empfaenger: dict[Art, list[Callable[[Ereignis], None]]] = {}

    def abonnieren(self, art: Art, empfaenger: Callable[[Ereignis], None]) -> Callable[[], None]:
        """Meldet ``empfaenger`` für eine Art an; gibt eine Funktion zum Abmelden zurück."""
        self._empfaenger.setdefault(art, []).append(empfaenger)
        return lambda: self._empfaenger.get(art, []).remove(empfaenger)

    def melden(self, ereignis: Ereignis) -> None:
        ausgang.pruefe(ereignis, "Ereignis")                      # nie ein Kern-Objekt an die Oberfläche
        for empfaenger in list(self._empfaenger.get(ereignis.art, [])):
            empfaenger(ereignis)


melder = Melder()
