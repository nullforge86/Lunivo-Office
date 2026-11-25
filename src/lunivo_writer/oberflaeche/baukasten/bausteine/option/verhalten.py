"""Verhalten des Optionsfeldes: Zustand, Aktivierung, Rückruf beim Umschalten und Gruppe (nur eine Option je Gruppe gewählt)."""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QAbstractButton, QButtonGroup


def verbinden(option: QAbstractButton, an: bool = False, aktion: Callable[[bool], object] | None = None, aktiv: bool = True,
              gruppe: QButtonGroup | None = None, nummer: int = -1) -> QAbstractButton:
    if gruppe is not None:
        gruppe.addButton(option, nummer)
    option.setChecked(an)
    option.setEnabled(aktiv)
    if aktion is not None:
        option.toggled.connect(lambda gesetzt: aktion(bool(gesetzt)))
    return option
