"""Form des Eingabefeldes: Mindesthöhe und Breite je Rolle – die eine Stelle dafür."""
from __future__ import annotations

from PySide6.QtWidgets import QWidget

from lunivo_writer.oberflaeche.baukasten.basis import mass as m

FORMEN: dict[str, tuple[int | None, int | None]] = {
    "standard": (m.HOEHE_KNOPF, None),        # Zeilenfeld wie die Knöpfe daneben
    "gross": (m.HOEHE_KNOPF_GROSS, None),     # Zeilenfeld neben großen Knöpfen
    "frei": (None, None),                     # wie das Thema es zeichnet
}


def formen(feld: QWidget, form: str) -> QWidget:
    hoehe, breite = FORMEN[form]
    if hoehe is not None:
        feld.setMinimumHeight(hoehe)
    if breite is not None:
        feld.setMinimumWidth(breite)
    return feld
