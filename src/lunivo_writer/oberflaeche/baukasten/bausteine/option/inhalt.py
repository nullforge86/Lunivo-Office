"""Inhalt des Optionsfeldes: Beschriftung, Quickinfo und Name für Bedienungshilfen."""
from __future__ import annotations

from PySide6.QtWidgets import QAbstractButton


def beschriften(option: QAbstractButton, text: str = "", tooltip: str = "", name: str = "") -> QAbstractButton:
    if text:
        option.setText(text)
    if tooltip:
        option.setToolTip(tooltip)
    option.setAccessibleName(name or tooltip or text.replace("&", ""))
    return option
