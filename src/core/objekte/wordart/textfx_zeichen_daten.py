"""Textfx zeichen daten: aus ``vcl.qt.rendering.wordart.textfx_zeichen`` herausgelöst."""
from __future__ import annotations


def _woerter(text: str) -> list[tuple[int, int]]:
    """Die Wörter eines Textes als (Anfang, Ende); Leerzeichen bleiben frei („Nur Wörter“)."""
    aus, start = [], None
    for i, ch in enumerate(text + " "):
        if ch.isspace():
            if start is not None:
                aus.append((start, i)); start = None
        elif start is None:
            start = i
    return aus
