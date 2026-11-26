"""Melder: Die Oberfläche abonniert Ereignisse ausschließlich hier; das Framework meldet sie. Rückrufe sind einfache Python-Funktionen."""
from __future__ import annotations

from collections.abc import Callable

from framework.pruefung import ausgangspruefung as ausgang
from framework.schnittstellen.datentypen.ereignisdaten import Art, Ereignis


class Melder:
    def __init__(self) -> None:
        self._empfaenger: dict[Art, list[Callable[[Ereignis], None]]] = {}
        self._abos: dict[int, tuple[Art, Callable[[Ereignis], None]]] = {}
        self._naechstes = 1

    def abonnieren(self, art: Art, empfaenger: Callable[[Ereignis], None]) -> int:
        """Meldet ``empfaenger`` für eine Art an; → Nummer des Abonnements (zum Abmelden mit ``abmelden``)."""
        self._empfaenger.setdefault(art, []).append(empfaenger)
        nummer, self._naechstes = self._naechstes, self._naechstes + 1
        self._abos[nummer] = (art, empfaenger)
        return nummer

    def abmelden(self, nummer: int) -> None:
        """Beendet das Abonnement mit der Nummer; ein unbekanntes oder schon beendetes wird übergangen."""
        abo = self._abos.pop(nummer, None)
        if abo is not None and abo[1] in self._empfaenger.get(abo[0], []):
            self._empfaenger[abo[0]].remove(abo[1])

    def melden(self, ereignis: Ereignis) -> None:
        ausgang.pruefe(ereignis, "Ereignis")                      # nie ein Kern-Objekt an die Oberfläche
        for empfaenger in list(self._empfaenger.get(ereignis.art, [])):
            empfaenger(ereignis)


melder = Melder()
