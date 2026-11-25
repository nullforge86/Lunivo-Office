"""Inhalt von Haken und Auswahlknopf: Beschriftung, Quickinfo und Name für Bedienungshilfen."""
from __future__ import annotations

from PySide6.QtWidgets import QAbstractButton


def beschriften(haken: QAbstractButton, text: str = "", tooltip: str = "", name: str = "") -> QAbstractButton:
    if text:
        haken.setText(text)
    if tooltip:
        haken.setToolTip(tooltip)
    haken.setAccessibleName(name or tooltip or text.replace("&", ""))
    return haken
