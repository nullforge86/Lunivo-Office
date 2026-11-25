from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPixmap
from vcl.qt.widgets.bausteine.farben import farben as F


def weitere_farben(parent, start=None, titel: str = "Farbe") -> QColor | None:
    """„Weitere Farben …“: das Fenster „Farben“ (Standard · Benutzerdefiniert · Erweitert). Gibt die Farbe zurück oder ``None`` bei Abbruch."""
    from vcl.qt.widgets.bausteine.interaktion.felder.farben_dialog import FarbenDialog
    d = FarbenDialog(parent, start, titel)
    if not d.exec():
        return None
    c = d.farbe()
    F.zuletzt_merken(c.name())
    return c


def farb_symbol(farbe: str | None, groesse: int = 14) -> QIcon:
    pm = QPixmap(groesse, groesse)
    pm.fill(QColor(farbe) if farbe else Qt.transparent)
    return QIcon(pm)
