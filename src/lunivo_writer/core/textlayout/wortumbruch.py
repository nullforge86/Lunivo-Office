"""Wortgrenzen: wo eine Zeile enden darf (Leerzeichen, Bindestriche, weiche Trennstellen). Ohne Qt, ohne Schrift."""
from __future__ import annotations

# Zeichen, nach denen eine Zeile enden darf (zusätzlich zum Leerzeichen): Bindestrich, Gedankenstrich, Schrägstrich, weicher Trennstrich, Nullbreitenleerzeichen
UMBRUCH_NACH = "-‐–—/­​"
LEERZEICHEN = " \t          　"        # geschütztes Leerzeichen (U+00A0) bricht nie


def umbruch_stellen(text: str) -> list[int]:
    """Stellen, an denen eine Zeile enden darf: der Index des ersten Zeichens der nächsten Zeile (nach Leerzeichen, Bindestrich usw.; Zeilenumbruch erzwingt)."""
    res = []
    for i, c in enumerate(text):
        if c == "\n" or c == " ":
            res.append(i + 1)
        elif i + 1 < len(text) and (c in LEERZEICHEN or c in UMBRUCH_NACH) and text[i + 1] not in LEERZEICHEN:
            res.append(i + 1)
    return res
