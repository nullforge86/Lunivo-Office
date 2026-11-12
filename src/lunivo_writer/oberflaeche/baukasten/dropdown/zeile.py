"""Dropdown-Zeile: die eine Gestalt jeder Zeilentaste in aufklappenden Fenstern (Menütafel, Raster, Galerie, Bildmenüs).

Aufrufer setzen kein Stylesheet: ``dropdown_zeile`` markiert die Taste, Abstand, Ausrichtung, Rand und Schrift stehen in ``oberflaeche/thema.py``
(Regel ``QPushButton[dropdownZeile]``, Maße aus ``mass.py``)."""
from __future__ import annotations

from PySide6.QtWidgets import QPushButton


def dropdown_zeile(taste: QPushButton, *, hinweis: bool = False) -> QPushButton:
    """Macht ``taste`` zur Dropdown-Zeile; ``hinweis``: kleinere Schrift (Hinweis-Zeilen wie „Zuletzt geöffnet“)."""
    taste.setFlat(True)
    taste.setProperty("dropdownZeile", "hinweis" if hinweis else "zeile")
    return taste
