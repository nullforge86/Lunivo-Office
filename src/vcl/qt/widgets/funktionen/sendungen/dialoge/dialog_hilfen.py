"""Gemeinsame Bausteine der Sendungen-Dialoge: Hinweiszeile und Knopfzeile."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel

from vcl.qt.widgets.bausteine.basis.dialog_rahmen import knopfzeile


def hinweis(text: str) -> QLabel:
    lb = QLabel(text.replace("\n", " "))
    lb.setWordWrap(True)
    return lb


def ok_zeile(dlg, text_ok: str | None = None):
    return knopfzeile(dlg, ok_text=text_ok or "OK")
