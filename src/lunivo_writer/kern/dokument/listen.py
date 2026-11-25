"""Listen und Nummerierung: Zahlenarten und die Marken (Nummer oder Aufzählungszeichen) aller Listenabsätze."""
from __future__ import annotations

from .dokument import AUFZAEHLUNGEN, LISTEN_EBENEN, Dokument

PLATZHALTER = "①②③④⑤⑥⑦⑧⑨"
ZEICHEN_DER_AUFZAEHLUNG = {"disc": "•", "circle": "◦", "square": "▪"}


def nummer_text(stil: str, n: int) -> str:
    """Die Zahl ``n`` in der Zahlenart ``stil`` (dezimal, klein, gross, roem_klein, roem_gross)."""
    if stil in ("klein", "gross"):
        s = ""
        while n > 0:
            n, r = divmod(n - 1, 26)
            s = chr(97 + r) + s
        return s if stil == "klein" else s.upper()
    if stil in ("roem_klein", "roem_gross"):
        s = ""
        for w, z in ((1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"), (50, "l"), (40, "xl"), (10, "x"), (9, "ix"),
                     (5, "v"), (4, "iv"), (1, "i")):
            while n >= w:
                s += z; n -= w
        return s if stil == "roem_klein" else s.upper()
    return str(n)


def listenmarken(dokument: Dokument) -> dict:
    """Absatz-Id → Text der Nummer oder des Aufzählungszeichens, für alle Listenabsätze in Dokumentreihenfolge."""
    marken: dict = {}
    staende: dict = {}                                   # Listen-Id → Zählerstände je Ebene
    for a in dokument.absaetze():
        definition = dokument.listen.get(a.liste_id) if a.liste_id is not None else None
        if definition is None or not definition.ebenen:
            continue
        e = min(max(a.ebene, 0), len(definition.ebenen) - 1)
        ebene = definition.ebenen[e]
        stand = staende.setdefault(definition.id, [None] * LISTEN_EBENEN)
        if "liste_start" in a.format:
            stand[e] = int(a.format["liste_start"])
        else:
            stand[e] = ebene.start if stand[e] is None else stand[e] + 1
        for tiefer in range(e + 1, LISTEN_EBENEN):
            stand[tiefer] = None
        if ebene.stil in AUFZAEHLUNGEN:
            marken[a.id] = ebene.zeichen or ZEICHEN_DER_AUFZAEHLUNG.get(ebene.stil, "•")
            continue
        text = ebene.format or (PLATZHALTER[e] + ".")
        for i, zeichen in enumerate(PLATZHALTER):
            if zeichen in text:
                hoehere = definition.ebenen[i] if i < len(definition.ebenen) else ebene
                wert = stand[i] if stand[i] is not None else hoehere.start
                stil = "dezimal" if (i != e and ebene.zusatz.get("norm")) or hoehere.stil in AUFZAEHLUNGEN else hoehere.stil
                text = text.replace(zeichen, nummer_text(stil, wert))
        marken[a.id] = text
    return marken
