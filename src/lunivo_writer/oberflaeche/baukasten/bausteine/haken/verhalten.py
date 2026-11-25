"""Verhalten von Haken und Auswahlknopf: Zustand, Aktivierung und Rückruf beim Umschalten."""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QAbstractButton


def verbinden(haken: QAbstractButton, an: bool = False, aktion: Callable[[bool], object] | None = None, aktiv: bool = True) -> QAbstractButton:
    haken.setChecked(an)
    haken.setEnabled(aktiv)
    if aktion is not None:
        haken.toggled.connect(lambda gesetzt: aktion(bool(gesetzt)))
    return haken
