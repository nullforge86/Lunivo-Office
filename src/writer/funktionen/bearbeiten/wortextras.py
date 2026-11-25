"""Wort-Extras: ordnet die Menüeinträge der Oberfläche den Framework-Befehlen zu."""
from __future__ import annotations

from framework.befehle import bearbeiten as _befehle
from framework.schnittstellen.datentypen import Menueeintrag


def wortextras_menue() -> tuple[Menueeintrag, ...]:
    return _befehle.MENUE


def wortextra_ausfuehren(kennung: int, befehl: str) -> int:
    """→ Zahl der geänderten Stellen (0, wenn nichts geändert wurde oder das Dokument schreibgeschützt ist)."""
    return _befehle.wortextra_ausfuehren(kennung, befehl) or 0
