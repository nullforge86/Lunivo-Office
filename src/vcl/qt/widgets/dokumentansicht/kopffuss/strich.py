"""Der gestrichelte graue Strich, mit dem Feldrahmen, Linie und Etikett der Kopf- und Fußzeile auf dem Blatt gezeichnet werden."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen

from vcl.qt.widgets.bausteine.farben import KOPFFUSS_RAHMEN


def strichstift() -> QPen:
    stift = QPen(QColor(KOPFFUSS_RAHMEN))
    stift.setStyle(Qt.DashLine)
    return stift
