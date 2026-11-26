"""Schriften für die Oberfläche: die Schriftfamilien der Schriftdatenbank des Kerns, über ``framework.anbindung.schriften``."""
from __future__ import annotations

import framework.anbindung.schriften as _fw


def familien() -> list[str]:
    """Die Namen aller Schriftfamilien, die der Kern setzen kann."""
    return list(_fw.familien())


def hat_familie(familie: str) -> bool:
    return _fw.hat_familie(familie)
