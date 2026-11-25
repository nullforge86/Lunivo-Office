"""Anzeige-Port für Befehle, die den Text ändern: Was die Qt-Ansicht des Editors dem Framework zur Verfügung stellt.

Die Oberfläche setzt diesen Vertrag um (``KernEditor`` erfüllt ihn strukturell). Die Bearbeitungssitzung wird als undurchsichtiges Objekt an die
übergebene Funktion gereicht und nur innerhalb des Frameworks und des Kerns benutzt."""
from __future__ import annotations

from collections.abc import Callable
from typing import Protocol


class AenderungsPort(Protocol):
    def aendern(self, aenderung: Callable[[object], object]) -> bool:
        """Führt ``aenderung(sitzung)`` als eine Änderung des Dokuments aus (Rückgängig-Schritt, Neuzeichnen); ``False``, wenn sie abgelehnt wird."""

    def lesen(self, abfrage: Callable[[object], object]):
        """Gibt ``abfrage(sitzung)`` zurück, ohne das Dokument zu ändern."""

    def page_settings_changed(self, seite: object) -> None:
        """Übernimmt die geänderte Seiteneinrichtung des Abschnitts an der Schreibmarke."""
