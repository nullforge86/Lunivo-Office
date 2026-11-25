"""Steuerung der offenen Dokumente des Hauptfensters: ordnet die Bedienaktionen den Sitzungsbefehlen des Frameworks zu."""
from __future__ import annotations

from framework.schnittstellen.datentypen.geoeffnet import Geoeffnet
from framework.sitzungen.dokumentsteuerung import sitzung


def neu(grundschrift: tuple[str, float] | None = None) -> int:
    return sitzung.neu(grundschrift)


def oeffnen_datei(pfad: str, kennwort: str | None = None) -> Geoeffnet:
    return sitzung.oeffnen_datei(pfad, kennwort)


def schliessen(kennung: int) -> None:
    sitzung.schliessen(kennung)


def aktivieren(kennung: int) -> None:
    sitzung.aktivieren(kennung)
