#!/usr/bin/env python3
"""Kontaktübersicht der Funktionssymbole als PNG:  python3 werkzeug/symbol-uebersicht.py [Ziel.png] [--dunkel]

Zeigt jedes Symbol aus assets/icons/symbole.json bei 16, 20 und 24 px (Qt-Rendering wie in der Anwendung),
darunter den Namen. Prüfhilfe für das Icon-System; schreibt kein HTML."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QImage, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from lunivo_writer.ui.widgets import icons  # noqa: E402


def uebersicht(ziel: str, dunkel: bool) -> int:
    namen = sorted(icons.pfade_original())
    hg, fg = ("#1f2328", "#e6e6e6") if dunkel else ("#ffffff", "#1f2328")
    spalten, zelle_b, zelle_h = 8, 150, 62
    zeilen = -(-len(namen) // spalten)
    img = QImage(spalten * zelle_b, zeilen * zelle_h, QImage.Format_ARGB32)
    img.fill(QColor(hg))
    p = QPainter(img)
    p.setFont(QFont("DejaVu Sans", 7))
    p.setPen(QColor(fg))
    for i, n in enumerate(namen):
        x, y = (i % spalten) * zelle_b + 6, (i // spalten) * zelle_h + 4
        for k, px in enumerate((16, 20, 24)):
            pm = icons.icon(n, px).pixmap(px, px)
            p.drawPixmap(x + k * 34, y, pm)
        p.drawText(x, y + 30, zelle_b - 8, 28, Qt.TextWordWrap, n)
    p.end()
    img.save(ziel)
    return len(namen)


if __name__ == "__main__":
    app = QApplication([])
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    dunkel = "--dunkel" in sys.argv
    ziel = a[0] if a else "symbol-uebersicht-dunkel.png" if dunkel else "symbol-uebersicht.png"
    print(uebersicht(ziel, dunkel), "Symbole ->", ziel)
