"""Gemeinsame Bausteine der Verweise-Dialoge."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel


def titel(text: str, feld) -> QLabel:
    """Beschriftung mit Tastenkürzel, die zum Feld springt."""
    t = QLabel(text)
    t.setBuddy(feld)
    return t
