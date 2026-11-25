"""Form des Eingabefeldes: Mindesthöhe und Breite je Rolle – die eine Stelle dafür."""
from __future__ import annotations

from PySide6.QtWidgets import QWidget

from vcl.qt.widgets.bausteine.abstaende import mass as m

FORMEN: dict[str, tuple[int | None, int | None]] = {
    "standard": (m.HOEHE_KNOPF, None),        # Zeilenfeld wie die Knöpfe daneben
    "gross": (m.HOEHE_KNOPF_GROSS, None),     # Zeilenfeld neben großen Knöpfen
    "frei": (None, None),                     # wie das Thema es zeichnet
    "zahl": (m.HOEHE_KNOPF_GROSS, m.BREITE_FELD_ZAHL),   # Feld mit einer Zahl: feste Breite
}
FESTE_BREITE = frozenset({"zahl"})            # Formen mit fester statt Mindestbreite


def formen(feld: QWidget, form: str) -> QWidget:
    hoehe, breite = FORMEN[form]
    if hoehe is not None:
        feld.setMinimumHeight(hoehe)
    if breite is not None:
        feld.setFixedWidth(breite) if form in FESTE_BREITE else feld.setMinimumWidth(breite)
    return feld
