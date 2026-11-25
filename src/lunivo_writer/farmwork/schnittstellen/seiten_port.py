"""Anzeige-Port für Befehle, die Seiteneinrichtungen ändern: Was die Qt-Ansicht des Editors dem Framework zur Verfügung stellt.

Die Oberfläche setzt diesen Vertrag um (``KernEditor`` erfüllt ihn strukturell); das Framework kennt nur diese Schnittstelle und nie die Oberfläche.
Die Seiteneinrichtung wird als undurchsichtiges Objekt weitergereicht und nur innerhalb des Frameworks verändert."""
from __future__ import annotations

from typing import Protocol


class SeitenPort(Protocol):
    def abschnitt_nr(self) -> int:
        """Nummer des Abschnitts an der Schreibmarke (ab 0)."""

    def abschnitt_seite(self, nr: int | None = None) -> object:
        """Kopie der Seiteneinrichtung des Abschnitts (ohne Angabe: an der Schreibmarke) zum Ändern."""

    def page_settings_changed(self, seite: object) -> None:
        """Übernimmt die geänderte Seiteneinrichtung des Abschnitts an der Schreibmarke."""

    def kopffuss(self) -> object:
        """Bearbeiter der Kopf- und Fußzeile (Zustand ``aktiv``, Zone, Navigation); ``None``, wenn es keinen gibt."""
