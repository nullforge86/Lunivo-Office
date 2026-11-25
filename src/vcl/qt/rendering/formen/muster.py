from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QImage, QPixmap
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.farben.farben import DURCHSICHTIG
from core.objekte.formen.muster_daten import _an


def kachel(schluessel: str, muster: str = Farbe.SCHWARZ, fuell: str | None = None) -> QPixmap:
    """Eine 8 × 8-Kachel des Musters; ohne Füllfarbe bleibt der Grund durchsichtig."""
    bild = QImage(8, 8, QImage.Format_ARGB32)
    grund = QColor(fuell) if fuell else QColor(*DURCHSICHTIG)
    vorn = QColor(muster)
    for y in range(8):
        for x in range(8):
            bild.setPixelColor(x, y, vorn if schluessel != "loeschen" and _an(schluessel, x, y) else grund)
    return QPixmap.fromImage(bild)


def pinsel(schluessel: str, muster: str = Farbe.SCHWARZ, fuell: str | None = None) -> QBrush:
    """Der Pinsel für den Hintergrund eines Absatzes (Muster über Füllfarbe)."""
    if schluessel in ("", "loeschen"):
        return QBrush(QColor(fuell)) if fuell else QBrush(Qt.NoBrush)
    return QBrush(kachel(schluessel, muster, fuell))
