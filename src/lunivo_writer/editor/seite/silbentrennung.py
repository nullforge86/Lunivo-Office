"""Silbentrennung für Druck, PDF und Seitenzählung: weiche Trennstriche (U+00AD) in einer Kopie des Dokuments."""
from __future__ import annotations

import re

from PySide6.QtGui import QTextBlock, QTextCursor, QTextDocument

WEICHER_STRICH = "­"
_WORT = re.compile(r"[^\W\d_]{6,}", re.UNICODE)
_TRENNER = {}


def _trenner(sprache: str):
    """pyphen-Wörterbuch (zwischengespeichert); None, wenn pyphen oder die Sprache fehlt."""
    if sprache not in _TRENNER:
        try:
            import pyphen
            _TRENNER[sprache] = pyphen.Pyphen(lang=sprache, left=2, right=3) if sprache in pyphen.LANGUAGES else None
        except ImportError:
            _TRENNER[sprache] = None
    return _TRENNER[sprache]


def _trennstellen(block: QTextBlock, trenner) -> list[int]:
    """Zeichenstellen im Dokument, an denen im Absatz ein weicher Strich eingefügt wird."""
    stellen = []
    for m in _WORT.finditer(block.text()):
        w = m.group()
        if w.isupper() or WEICHER_STRICH in w:
            continue
        stellen.extend(block.position() + m.start() + i for i in trenner.positions(w))
    return stellen


def _einfuegen(d: QTextDocument, stellen: list[int]) -> int:
    c = QTextCursor(d)
    for pos in reversed(stellen):                       # von hinten, damit die Stellen davor gültig bleiben
        c.setPosition(pos)
        c.insertText(WEICHER_STRICH)
    return len(stellen)


def silben_einfuegen(d: QTextDocument, sprache: str) -> int:
    """Fügt in einer KOPIE des Dokuments weiche Trennstriche (U+00AD) in lange Wörter ein; Qt bricht dort um und zeigt „-“.
    Überschriften, Wörter mit Ziffern/Sonderzeichen und Verweise bleiben unberührt. → Anzahl eingefügter Trennstellen."""
    t = _trenner(sprache)
    if t is None:
        return 0
    n = 0
    b = d.firstBlock()
    while b.isValid():
        if b.blockFormat().headingLevel() == 0 and b.isVisible():
            n += _einfuegen(d, _trennstellen(b, t))
        b = b.next()
    return n
