"""Orte (Ordner) für die Oberfläche: Programmdaten und nachgeladene Schriften. Die Oberfläche fragt Pfade nur hier und nie bei der Infrastruktur."""
from __future__ import annotations

from lunivo_writer.infrastruktur.pfade import pfade


def data_dir() -> str:
    """Programmdaten des Benutzers; wird bei Bedarf angelegt."""
    return pfade.data_dir()


def schriften_dir() -> str:
    """Ordner der nachgeladenen Lese-Schriften."""
    return pfade.schriften_dir()
