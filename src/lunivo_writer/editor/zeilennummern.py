"""Zeilennummern (Seitenlayout ▸ Zeilennummern): welche Zeile welche Nummer trägt. Keine Oberfläche — Editor, Druck und PDF zeichnen damit.

    for block, zeile, y, nr in nummern(doc, ch, "seite"): …

``art``: "" fortlaufend durch das ganze Dokument, "seite" auf jeder Seite neu ab 1. Absätze mit „Zeilennummern unterdrücken“
(``absatzopt`` „ohne_zeilennr“, DOCX ``w:suppressLineNumbers``) bekommen keine Nummer und werden nicht mitgezählt.
"""
from __future__ import annotations

from typing import Iterator

from PySide6.QtGui import QTextBlock, QTextDocument, QTextLine

ARTEN = {"": "Fortlaufend", "seite": "Jede Seite neu beginnen"}


def unterdrueckt(block: QTextBlock) -> bool:
    from lunivo_writer.editor import absatzopt
    return absatzopt.lesen(block.blockFormat())["ohne_zeilennr"]


def nummern(doc: QTextDocument, ch: float, art: str = "") -> Iterator[tuple[QTextBlock, QTextLine, float, int]]:
    """(Absatz, Zeile, y im Textfluss, Nummer) für jede nummerierte Zeile; ``ch``: Höhe des Textbereichs einer Seite im Fluss."""
    lay = doc.documentLayout()
    nr, seite = 0, 0
    b = doc.firstBlock()
    while b.isValid():
        if b.isVisible() and b.layout() is not None and not unterdrueckt(b):
            top = lay.blockBoundingRect(b).top()
            for i in range(b.layout().lineCount()):
                z = b.layout().lineAt(i)
                y = top + z.y()
                if art == "seite" and ch > 0 and int((y + 1.0) // ch) != seite:
                    seite, nr = int((y + 1.0) // ch), 0
                nr += 1
                yield b, z, y, nr
        b = b.next()
