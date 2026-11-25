"""Inhalt des Rahmens: Objektname (für das Thema) und die Kartenart aus ``basis/karte.py``."""
from __future__ import annotations

from PySide6.QtWidgets import QFrame

from lunivo_writer.oberflaeche.baukasten.basis.karte import als_karte


def beschriften(rahmen: QFrame, name: str = "", karte: str = "") -> QFrame:
    if name:
        rahmen.setObjectName(name)
    if karte:
        als_karte(rahmen, karte)
    return rahmen
