"""Kleine, selbst gezeichnete Texturen für Vorschau und Füllung. Ohne Oberfläche."""
from __future__ import annotations

from PySide6.QtGui import QColor, QPainter, QPixmap


def textur(name: str, groesse: int = 26) -> QPixmap:
    """Eine kleine, selbst gezeichnete Textur (Vorschau und Füllung): ``papier``, ``granit``, ``holz``, ``stoff``, ``marmor``, ``sand``."""
    import random
    rnd = random.Random(name)
    pm = QPixmap(groesse, groesse)
    basis = {"papier": QColor("#f1ead8"), "granit": QColor("#9a9a9a"), "holz": QColor("#c8955a"), "stoff": QColor("#8aa4c8"),
             "marmor": QColor("#e6e6ea"), "sand": QColor("#e3cf9f")}[name]
    pm.fill(basis)
    p = QPainter(pm)
    for _ in range(groesse * 3):
        x, y = rnd.randrange(groesse), rnd.randrange(groesse)
        d = rnd.randint(-28, 28)
        p.setPen(QColor(max(0, min(255, basis.red() + d)), max(0, min(255, basis.green() + d)), max(0, min(255, basis.blue() + d))))
        if name == "holz":
            p.drawLine(0, y, groesse, y + rnd.randint(-1, 1))
        elif name == "stoff":
            p.drawLine(x, 0, x, groesse); p.drawLine(0, y, groesse, y)
        else:
            p.drawPoint(x, y)
    p.end()
    return pm
