"""Ergebnis des Öffnens einer Datei: die Kennung der neuen Sitzung und die Hinweise, was nicht übernommen werden konnte."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Geoeffnet:
    kennung: int
    hinweise: tuple[str, ...] = ()
