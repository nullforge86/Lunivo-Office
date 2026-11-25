"""Anzeige-Port für die Vorschau im Dokumentfenster (Original ohne Markup, Seriendruck-Vorschau): was die Oberfläche dem Farmwork anbietet.

Das Dokument, das gezeigt werden soll, wird als undurchsichtiges Objekt übergeben; die Oberfläche stellt es nur dar. Eine vollständige Anzeige-Pipeline
(Zeichenliste statt Dokumentobjekt) ersetzt diesen Weg später."""
from __future__ import annotations

from typing import Protocol


class VorschauPort(Protocol):
    def zeigen(self, dokument: object, art: str) -> None:
        """Zeigt ``dokument`` schreibgeschützt anstelle des Textes; ``art`` benennt die Vorschau (``original``, ``serien``)."""

    def aktiv(self, art: str) -> bool:
        """Läuft gerade eine Vorschau dieser Art?"""

    def beenden(self) -> None:
        """Beendet die Vorschau und zeigt wieder den Text."""
