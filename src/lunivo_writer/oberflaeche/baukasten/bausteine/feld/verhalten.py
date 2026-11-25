"""Verhalten des Eingabefeldes: nur lesen, Rückruf bei Änderung und bei Eingabetaste."""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QLineEdit


def verbinden(feld: QLineEdit, nur_lesen: bool = False, bei_aenderung: Callable[[str], object] | None = None,
              bei_eingabe: Callable[[], object] | None = None, passwort: bool = False, aktiv: bool = True) -> QLineEdit:
    feld.setReadOnly(nur_lesen)
    if passwort:
        feld.setEchoMode(QLineEdit.Password)
    feld.setEnabled(aktiv)
    if bei_aenderung is not None:
        feld.textChanged.connect(lambda text: bei_aenderung(text))
    if bei_eingabe is not None:
        feld.returnPressed.connect(lambda: bei_eingabe())
    return feld
