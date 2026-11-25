"""Die Textstücke eines Absatzes (``QTextBlock.begin()``) in einem eigenständigen Qt-Textfeld (``QTextEdit``, ``QTextBrowser``) der Reihe nach — Hilfsmittel der
Oberfläche für Eingabe- und Anzeigefelder, kein Teil der Dokumentverarbeitung.

    for f in absatz_fragmente(block): …            # gültige Stücke des Absatzes (``block`` aus ``feld.document()``)

Der Erzeuger liest nur. Wer beim Durchgehen den Text ändert, sammelt die Stellen erst (``list(...)``) und ändert danach.
"""
from __future__ import annotations

from typing import Iterator


def absatz_fragmente(block) -> Iterator:
    it = block.begin()
    while not it.atEnd():
        f = it.fragment()
        if f.isValid():
            yield f
        it += 1
