"""Der Piktogramm-Katalog (Name → 24×24-Pfad) und das Bild eines Piktogramms — neutral, ohne Oberfläche.

Gebraucht von ``editor/einfuegen.py`` (Piktogramm ins Dokument) und von ``ui/widgets/icons.py`` (Symbole der Oberfläche).
Gezeichnet wird mit ``QPainter`` und ``QSvgRenderer``; das SVG entsteht nur im Speicher als Zeichenvorschrift für den Renderer.
"""
from __future__ import annotations

import json
import os

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

from lunivo_writer.core import paths

STRICH = 1.05         # schlanke Office-Kontur bei typischen Symbolgrößen von 16–20 px
_KATALOG: dict | None = None


def katalog() -> dict:
    """Alle 1800 Lucide-Symbole (Name → 24×24-Pfad) — für Piktogramm einfügen und Symbol austauschen."""
    global _KATALOG
    if _KATALOG is None:
        with open(os.path.join(paths.SYMBOLE, "symbolkatalog.json"), encoding="utf-8") as fh:
            _KATALOG = json.load(fh)
    return _KATALOG


def katalog_bild(name: str, px: int = 96, farbe: str | None = None, strich: float = STRICH) -> QImage:
    from lunivo_writer.core.farben import Farbe
    farbe = farbe or Farbe.SYMBOL
    img = QImage(px, px, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    d = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{farbe}" stroke-width="{strich}" '
         f'stroke-linecap="round" stroke-linejoin="round"><path d="{katalog()[name]}"/></svg>').encode()
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(QByteArray(d)).render(p, QRectF(0, 0, px, px))
    p.end()
    return img
