"""Anzeige-Port für Abfragen über die frei positionierten Objekte: Was die Qt-Ansicht des Editors dem Framework zur Verfügung stellt.

Die Oberfläche setzt diesen Vertrag um (``KernEditor`` erfüllt ihn strukturell)."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class FreieObjektePort(Protocol):
    def _frei_liste(self) -> Sequence[tuple]:
        """(Schlüssel, Angabe, Bild, Rechteck, hinten, Seite) der frei positionierten Objekte in Dokumentreihenfolge."""
