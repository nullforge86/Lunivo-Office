"""Anbindung an die Schriftdatenbank des Kerns (``core.formatierung.schrift``): welche Schriftfamilien es gibt."""
from __future__ import annotations

from core.formatierung.schrift import standard_datenbank as _db


def familien() -> tuple[str, ...]:
    """Die Namen aller Schriftfamilien, die der Kern setzen kann."""
    return tuple(_db.familien())


def hat_familie(familie: str) -> bool:
    return _db.hat_familie(familie)
