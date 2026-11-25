"""Verweise: liefert der Oberfläche die Befehle des Frameworks für ein Dokument (Kennung)."""
from __future__ import annotations

from framework.befehle.verweise import VerweiseBefehle
from framework.ereignisse import Melder
from framework.schnittstellen import Einstellungen


def verweise_befehle(kennung: int, einstellungen: Einstellungen | None = None, melder: Melder | None = None) -> VerweiseBefehle:
    return VerweiseBefehle(kennung, einstellungen, melder)
