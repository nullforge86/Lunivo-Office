"""Anzeige-Port für die Vorschau im Dokumentfenster (Original ohne Markup, Seriendruck-Vorschau): was die Oberfläche dem Farmwork anbietet.

Das Dokument, das gezeigt werden soll, legt das Framework als Nebendokument an und übergibt nur dessen Kennung; die Oberfläche stellt es dar
und gibt es beim Beenden wieder frei."""
from __future__ import annotations

from typing import Protocol


class VorschauPort(Protocol):
    def zeigen(self, kennung: int, art: str) -> None:
        """Zeigt das Nebendokument ``kennung`` schreibgeschützt anstelle des Textes; ``art`` benennt die Vorschau (``original``, ``serien``)."""

    def aktiv(self, art: str) -> bool:
        """Läuft gerade eine Vorschau dieser Art?"""

    def beenden(self) -> None:
        """Beendet die Vorschau und zeigt wieder den Text."""
