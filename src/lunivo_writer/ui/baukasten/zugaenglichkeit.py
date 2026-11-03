"""Zugängliche Namen für Knöpfe ohne eigenen Namen (Screenreader, Sprachsteuerung).

Ein Knopf, der nur ein Symbol oder ein Kürzel zeigt (↘, ›, Zoom-Pfeil), bekommt beim ersten Anzeigen seinen Tooltip als Namen,
ohne die Tastenkombination in Klammern. Vorhandene Namen bleiben unberührt.

    NamenFilter.einhaengen(app)         # einmal beim Start
"""
from __future__ import annotations

import re

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QAbstractButton, QApplication

_KUERZEL = re.compile(r"\s*[(—–].*$")             # „Öffnen (Strg+O)“ → „Öffnen“, „Prüfen (F7) — sucht …“ → „Prüfen“


def name_fuer(knopf: QAbstractButton) -> str:
    """Der Name, den ein Screenreader für diesen Knopf lesen soll: Text, sonst Tooltip, ohne Tastenkombination und Erklärung."""
    text = " ".join(knopf.text().replace("&", "").split())
    if len(text) > 2 and any(c.isalpha() for c in text):
        return text
    tip = _KUERZEL.sub("", knopf.toolTip().strip())
    return tip or text


class NamenFilter(QObject):
    """Setzt beim ersten Anzeigen eines Knopfes den zugänglichen Namen, wenn noch keiner gesetzt ist."""

    def eventFilter(self, obj, ev):
        if ev.type() == QEvent.Show and isinstance(obj, QAbstractButton) and not obj.accessibleName():
            name = name_fuer(obj)
            if name:
                obj.setAccessibleName(name)
        return False

    @classmethod
    def einhaengen(cls, app: QApplication) -> "NamenFilter":
        f = cls(app)
        app.installEventFilter(f)
        return f
