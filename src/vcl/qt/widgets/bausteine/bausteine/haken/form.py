"""Form von Haken und Auswahlknopf (Kontrollkästchen, Optionsfeld): Mindesthöhe je Rolle – die eine Stelle dafür."""
from __future__ import annotations

from PySide6.QtWidgets import QAbstractButton

from writer.baukasten.basis import mass as m

FORMEN: dict[str, int | None] = {
    "standard": None,                  # wie das Thema ihn zeichnet
    "zeile": m.HOEHE_KNOPF,            # eigene Zeile mit Luft (Listen von Haken)
}


def formen(haken: QAbstractButton, form: str) -> QAbstractButton:
    hoehe = FORMEN[form]
    if hoehe is not None:
        haken.setMinimumHeight(hoehe)
    return haken
