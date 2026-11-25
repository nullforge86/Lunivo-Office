"""Meldet dem Kern die Orte an, die er braucht (Programmdaten, Vorlagenordner, Schriftordner); der Kern liest nicht aus ``system``."""
from __future__ import annotations

from core.dokument import orte
from system.plattform import pfade, ressourcen_pfade
from system.plattform.schriften import schrift_ordner


def anmelden() -> None:
    orte.anmelden(ressourcen_pfade.RESSOURCEN, pfade.vorlagen_dir, schrift_ordner)
