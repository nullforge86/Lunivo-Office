"""Verhalten des Rahmens: sichtbar und eine Eigenschaft für das Thema (zum Beispiel ``fokus`` beim Eingabekasten)."""
from __future__ import annotations

from PySide6.QtWidgets import QFrame


def verbinden(rahmen: QFrame, sichtbar: bool = True, eigenschaften: dict[str, object] | None = None) -> QFrame:
    for schluessel, wert in (eigenschaften or {}).items():
        rahmen.setProperty(schluessel, wert)
    if not sichtbar:
        rahmen.setVisible(False)
    return rahmen
