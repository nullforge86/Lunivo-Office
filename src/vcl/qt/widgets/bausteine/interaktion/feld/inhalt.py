"""Inhalt des Eingabefeldes: Text, Platzhalter und Name für Bedienungshilfen."""
from __future__ import annotations

from PySide6.QtWidgets import QLineEdit


def beschriften(feld: QLineEdit, text: str = "", platzhalter: str = "", name: str = "") -> QLineEdit:
    if text:
        feld.setText(text)
    if platzhalter:
        feld.setPlaceholderText(platzhalter)
    if name:
        feld.setAccessibleName(name)
    return feld
