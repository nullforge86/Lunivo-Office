"""Form des Optionsfeldes (Auswahlknopf): Mindesthöhe je benannter Form – die eine Stelle dafür."""
from __future__ import annotations

from PySide6.QtWidgets import QAbstractButton

from lunivo_writer.oberflaeche.baukasten.basis import mass as m

FORMEN: dict[str, int | None] = {
    "standard": None,                  # wie das Thema es zeichnet
    "zeile": m.HOEHE_KNOPF,            # eigene Zeile mit Luft (Listen von Optionen)
}


def formen(option: QAbstractButton, form: str) -> QAbstractButton:
    hoehe = FORMEN[form]
    if hoehe is not None:
        option.setMinimumHeight(hoehe)
    return option
