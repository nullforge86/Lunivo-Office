"""Die Textstücke (``QTextFragment``) eines Absatzes oder des ganzen Dokuments der Reihe nach — die eine Stelle für diese Schleife.

    for f in absatz_fragmente(b): …            # gültige Stücke eines Absatzes
    for f in dokument_fragmente(doc): …        # alle Absätze, in Textreihenfolge

Die Erzeuger lesen nur. Wer beim Durchgehen den Text ändert, sammelt die Stellen erst (``list(...)``) und ändert danach.
"""
from __future__ import annotations

from typing import Iterator

from PySide6.QtGui import QTextBlock, QTextDocument, QTextFragment


def absatz_fragmente(b: QTextBlock) -> Iterator[QTextFragment]:
    it = b.begin()
    while not it.atEnd():
        f = it.fragment()
        if f.isValid():
            yield f
        it += 1


def dokument_fragmente(doc: QTextDocument) -> Iterator[QTextFragment]:
    b = doc.firstBlock()
    while b.isValid():
        yield from absatz_fragmente(b)
        b = b.next()
