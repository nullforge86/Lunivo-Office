"""Die Grundfarben des Programms für die Oberfläche: eine unveränderliche Kopie der Werte des Kerns (Name → Farbwert).

Die Oberfläche baut daraus ihre eigene Farbtafel; was ein Farbthema dort umstellt, bleibt in der Oberfläche und erreicht den Kern nicht."""
from __future__ import annotations

from collections.abc import Mapping

from framework.schnittstellen.datentypen import grundfarben as _grundfarben


def grundfarben() -> Mapping[str, str | None | tuple | Mapping[str, str]]:
    """Name → Wert (Farbtext, ``None``, Folgen als Tupel, Tafeln als schreibgeschützte Wörterbücher) aller Grundfarben."""
    return _grundfarben()
