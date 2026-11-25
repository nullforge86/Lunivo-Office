"""Einfuegen fenster hilfen: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster`` herausgelöst."""
from __future__ import annotations
from PySide6.QtWidgets import QLabel


def _titel(text: str, feld) -> QLabel:
    t = QLabel(text); t.setBuddy(feld)
    return t
