"""Sitzung: offene Dokumente und das aktive Dokument. Nach außen gibt es nur Nummern (``int``) der Dokumente, nie Kern-Objekte.

Die Qt-freien Teile von ``anwendung.py`` und ``dokument_verwaltung.py`` kommen schrittweise hierher (Übergang: ``NOCH_NICHT_UMGESTELLT``)."""
from __future__ import annotations

from framework.datentypen.ereignisdaten import Art, Ereignis
from framework.steuerung.ereignissteuerung import melder


class Sitzung:
    def __init__(self) -> None:
        self._dokumente: dict[int, object] = {}                 # privat: Kern-Dokumente bleiben im Framework
        self._aktiv: int | None = None
        self._naechste = 1

    def oeffnen(self, dokument: object) -> int:
        nummer = self._naechste
        self._naechste += 1
        self._dokumente[nummer] = dokument
        self._aktiv = nummer
        melder.melden(Ereignis(Art.GEAENDERT, "dokument_geoeffnet", {"nummer": nummer}))
        return nummer

    def schliessen(self, nummer: int) -> None:
        self._dokumente.pop(nummer, None)
        if self._aktiv == nummer:
            self._aktiv = next(reversed(self._dokumente), None)
        melder.melden(Ereignis(Art.GEAENDERT, "dokument_geschlossen", {"nummer": nummer}))

    def aktivieren(self, nummer: int) -> None:
        if nummer in self._dokumente:
            self._aktiv = nummer
            melder.melden(Ereignis(Art.GEAENDERT, "dokument_aktiv", {"nummer": nummer}))

    @property
    def aktiv(self) -> int | None:
        return self._aktiv

    @property
    def offene(self) -> tuple[int, ...]:
        return tuple(self._dokumente)

    def _dokument(self, nummer: int | None = None) -> object | None:
        """Nur für das Framework selbst (``funktionen/<name>/befehle.py``)."""
        return self._dokumente.get(self._aktiv if nummer is None else nummer)


sitzung = Sitzung()
