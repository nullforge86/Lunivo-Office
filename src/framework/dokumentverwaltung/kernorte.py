"""Meldet dem Kern die Orte an, die er braucht (Programmdaten, Vorlagenordner, Schriftordner); der Kern liest nicht aus ``system``."""
from __future__ import annotations

from core.dokument import orte
from system import pfade


def anmelden() -> None:
    orte.anmelden(pfade.RESSOURCEN, pfade.vorlagen_dir, pfade.schrift_ordner)
