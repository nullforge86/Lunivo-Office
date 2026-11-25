"""Formular gitter hilfen: aus ``vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter`` herausgelöst."""
from __future__ import annotations
from PySide6.QtWidgets import QLayoutItem


def _natuerlich(item: QLayoutItem) -> int:
    w = item.widget()
    if w is not None and hasattr(w, "natuerliche_breite"):             # ein Widget mit Umbruch (Policy „Ignored“) meldet über das Layout sonst Breite 0
        return w.natuerliche_breite()
    return max(item.sizeHint().width(), item.minimumSize().width())
