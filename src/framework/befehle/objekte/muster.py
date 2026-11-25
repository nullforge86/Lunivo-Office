"""Muster der Schattierung und der Musterfüllung: Auswahlliste und Anzeigenamen. Die Fachdaten liegen im Kern; die Oberfläche erhält unveränderliche Werte."""
from __future__ import annotations

from core.objekte.formen import muster_daten as modell

MUSTER: tuple[tuple[str, str, str], ...] = tuple((schluessel, name, ooxml) for schluessel, name, ooxml in modell.MUSTER)   # (Schlüssel, Anzeigename, OOXML-Wert)


def name_von(schluessel: str) -> str:
    """Der Anzeigename eines Musters (unbekannte Schlüssel bleiben, wie sie sind)."""
    return modell.name_von(schluessel)
