"""Form des Rahmens: Rahmenart und Schatten je benannter Form – die eine Stelle dafür. Linienbreite, Radius und Farbe stehen im Thema bzw. in ``basis/karte.py``."""
from __future__ import annotations

from PySide6.QtWidgets import QFrame

# Form → (Rahmenart, Schatten)
FORMEN: dict[str, tuple[QFrame.Shape, QFrame.Shadow]] = {
    "flach": (QFrame.NoFrame, QFrame.Plain),                   # ohne Rahmen (Fläche, Kartengrund über ``karte``)
    "panel": (QFrame.StyledPanel, QFrame.Plain),               # Rahmen, wie das Thema ihn zeichnet (Kasten, Karte, Gruppe)
    "linie_waagerecht": (QFrame.HLine, QFrame.Sunken),         # Trennlinie quer
    "linie_senkrecht": (QFrame.VLine, QFrame.Sunken),          # Trennlinie hoch
}


def formen(rahmen: QFrame, form: str) -> QFrame:
    shape, shadow = FORMEN[form]
    rahmen.setFrameShape(shape)
    if shape in (QFrame.HLine, QFrame.VLine):
        rahmen.setFrameShadow(shadow)
    return rahmen
