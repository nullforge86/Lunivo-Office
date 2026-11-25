"""Bidirektionaler Text (Unicode-Algorithmus UAX #9, ohne Qt und ohne fremde Bibliothek): Ebenen der Zeichen eines Absatzes und die Anzeigereihenfolge
einer Zeile.

Umgesetzt sind die schwachen Regeln W1–W7, die neutralen Regeln N1–N2 und die impliziten Ebenen I1–I2 sowie die Zeilenregeln L1 und L2. Ausdrückliche
Einbettungen und Isolate (LRE, RLE, LRI …) gelten als neutrale Zeichen; Klammerpaare (N0) werden nicht gespiegelt. Texte ohne Zeichen der Klassen R und AL
(Hebräisch, Arabisch, …) brauchen keine Umordnung: ``ebenen`` liefert dafür ``None``.
"""
from __future__ import annotations

import unicodedata

STARK_RECHTS = ("R", "AL")
NEUTRAL = ("B", "S", "WS", "ON", "LRE", "RLE", "LRO", "RLO", "PDF", "LRI", "RLI", "FSI", "PDI")


def klassen(text: str) -> list:
    return [unicodedata.bidirectional(c) or "L" for c in text]


def hat_rechts_nach_links(text: str) -> bool:
    return any(unicodedata.bidirectional(c) in STARK_RECHTS for c in text)


def basis_ebene(text: str, richtung: str | None = None) -> int:
    """0 (links nach rechts) oder 1 (rechts nach links): ausdrücklich nach ``richtung`` („ltr“/„rtl“), sonst nach dem ersten starken Zeichen."""
    if richtung == "rtl":
        return 1
    if richtung == "ltr":
        return 0
    for k in klassen(text):
        if k == "L":
            return 0
        if k in STARK_RECHTS:
            return 1
    return 0


def ebenen(text: str, richtung: str | None = None):
    """(Ebene je Zeichen, Basisebene) des Absatzes — ``None``, wenn weder der Text noch die Richtung rechts nach links verlangt."""
    if richtung != "rtl" and not hat_rechts_nach_links(text):
        return None
    basis = basis_ebene(text, richtung)
    t = klassen(text)
    n = len(t)
    sos = "R" if basis else "L"
    # W1: nicht spationierende Zeichen erben die Klasse des Vorgängers
    for i in range(n):
        if t[i] == "NSM":
            t[i] = t[i - 1] if i else sos
    # W2: Europäische Ziffern nach arabischen Buchstaben werden arabische Ziffern; W3: AL wird R
    letzte = sos
    for i in range(n):
        if t[i] in ("L", "R", "AL"):
            letzte = t[i]
        elif t[i] == "EN" and letzte == "AL":
            t[i] = "AN"
    t = ["R" if k == "AL" else k for k in t]
    # W4: einzelner Trenner zwischen gleichen Ziffern
    for i in range(1, n - 1):
        if t[i] == "ES" and t[i - 1] == "EN" and t[i + 1] == "EN":
            t[i] = "EN"
        elif t[i] == "CS" and t[i - 1] == t[i + 1] and t[i - 1] in ("EN", "AN"):
            t[i] = t[i - 1]
    # W5: Abschlusszeichen neben europäischen Ziffern
    i = 0
    while i < n:
        if t[i] == "ET":
            j = i
            while j < n and t[j] == "ET":
                j += 1
            if (i > 0 and t[i - 1] == "EN") or (j < n and t[j] == "EN"):
                for k in range(i, j):
                    t[k] = "EN"
            i = j
        else:
            i += 1
    # W6: übrige Trenner und Abschlusszeichen werden neutral; W7: europäische Ziffern nach L werden L
    t = ["ON" if k in ("ES", "ET", "CS") else k for k in t]
    letzte = sos
    for i in range(n):
        if t[i] in ("L", "R"):
            letzte = t[i]
        elif t[i] == "EN" and letzte == "L":
            t[i] = "L"
    # N1/N2: neutrale Folgen zwischen gleichen Richtungen nehmen sie an, sonst die Basisrichtung
    def richtung_von(k: str) -> str:
        return "R" if k in ("R", "EN", "AN") else "L"
    i = 0
    while i < n:
        if t[i] in NEUTRAL or t[i] in ("BN",):
            j = i
            while j < n and (t[j] in NEUTRAL or t[j] == "BN"):
                j += 1
            davor = richtung_von(t[i - 1]) if i else sos
            danach = richtung_von(t[j]) if j < n else sos
            wert = davor if davor == danach else sos
            for k in range(i, j):
                t[k] = wert
            i = j
        else:
            i += 1
    # I1/I2: implizite Ebenen
    e = []
    for k in t:
        if basis == 0:
            e.append(0 if k == "L" else 1 if k == "R" else 2)
        else:
            e.append(1 if k == "R" else 2)
    return e, basis


def zeilen_reihenfolge(text: str, e: list, basis: int, start: int, ende: int) -> list:
    """Die Zeichenstellen ``start`` bis ``ende`` (ausschließlich) einer Zeile in Anzeigereihenfolge von links nach rechts (L1, L2)."""
    stellen = list(range(start, ende))
    if not stellen:
        return []
    ebene = [e[i] for i in stellen]
    k = len(ebene)
    while k > 0 and (text[stellen[k - 1]].isspace() or text[stellen[k - 1]] in "\n "):      # L1: Leerraum am Zeilenende hat die Basisebene
        ebene[k - 1] = basis
        k -= 1
    hoechste, niedrigste_ungerade = max(ebene), min((x for x in ebene if x % 2), default=None)
    if niedrigste_ungerade is None:
        return stellen
    for stufe in range(hoechste, niedrigste_ungerade - 1, -1):
        i = 0
        while i < len(stellen):
            if ebene[i] >= stufe:
                j = i
                while j < len(stellen) and ebene[j] >= stufe:
                    j += 1
                stellen[i:j] = stellen[i:j][::-1]
                ebene[i:j] = ebene[i:j][::-1]
                i = j
            else:
                i += 1
    return stellen
