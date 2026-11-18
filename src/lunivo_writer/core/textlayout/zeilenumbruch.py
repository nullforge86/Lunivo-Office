"""Zeilenumbruch aus den Vorschüben der Zeichen: Wortumbruch, zu lange Wörter brechen an der Zeichengrenze. Ohne Qt."""
from __future__ import annotations

from .engine import LineBox
from .wortumbruch import LEERZEICHEN, umbruch_stellen


def zeilen_umbrechen(text: str, vorschuebe: list[float], breite: float, hoehe: float, steig: float) -> list[LineBox]:
    """Zeilen aus den Vorschüben: Wortumbruch, ein zu langes Wort bricht an der Zeichengrenze. Leerzeichen am Zeilenende zählen nicht zur Breite."""
    if not text:
        return [LineBox(0, 0, 0.0, hoehe, steig)]
    zeilen: list[LineBox] = []
    erlaubt = set(umbruch_stellen(text))
    n = len(text)
    start = 0
    while start < n:
        x, ende, letzte = 0.0, start, None
        i = start
        zwang = False
        while i < n:
            c = text[i]
            if c == "\n" or c == " ":
                ende, zwang = i + 1, True
                break
            w = vorschuebe[i]
            sichtbar = x + w if c not in LEERZEICHEN else x                      # Leerzeichen am Zeilenende dürfen überstehen
            if sichtbar > breite + 0.01 and i > start:
                break
            x += w
            i += 1
            if i in erlaubt:
                letzte = i
        else:
            ende = n
        if not zwang and i < n:
            ende = letzte if letzte is not None and letzte > start else max(i, start + 1)
        elif not zwang:
            ende = n
        sicht_ende = ende - 1 if zwang else ende
        while sicht_ende > start and text[sicht_ende - 1] in LEERZEICHEN:
            sicht_ende -= 1
        w = sum(vorschuebe[start:sicht_ende])
        zeilen.append(LineBox(start, ende - start, w, hoehe, steig))
        start = ende
    if text[-1] in "\n ":
        zeilen.append(LineBox(n, 0, 0.0, hoehe, steig))
    return zeilen
