"""Zwischenablage: Text in die Zwischenablage legen — die eine Stelle dafür im Baukasten (Chat-Blasen u. a.)."""
from __future__ import annotations

from PySide6.QtWidgets import QApplication


def in_zwischenablage(text: str) -> None:
    QApplication.clipboard().setText(text)
