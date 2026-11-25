"""Wortgenaue Änderungen zwischen KI-Ergebnis und Ausgangstext."""

import difflib
import re

# ---------------------------------------------------------------- Ergebnis ins Dokument: Wort-Diff
_STUECKE = re.compile(r"\s+|[^\s]+")


def aenderungen(alt: str, neu: str):
    """Welche Wörter haben sich geändert? → [{von, bis, text}] in „alt"-Zeichenstellen; None, wenn zu groß."""
    a, b = _STUECKE.findall(alt), _STUECKE.findall(neu)
    if len(a) * len(b) > 400000:
        return None
    pos = [0]
    for s in a:
        pos.append(pos[-1] + len(s))
    blocks = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            blocks.append({"von": pos[i1], "bis": pos[i2], "text": "".join(b[j1:j2])})
    return blocks


def ersetze_ergebnis(alt: str, neu: str):
    """→ (liste_von_ersetzungen (von, bis, text) von hinten nach vorn, ganz: bool, absaetze)."""
    az, nz = alt.split("\n"), neu.split("\n")
    if len(az) != len(nz):
        return [(0, len(alt), neu)], True, 0
    ops, stelle, geaendert = [], len(alt), 0
    for i in range(len(az) - 1, -1, -1):
        anfang = stelle - len(az[i])
        if az[i] != nz[i]:
            blocks = aenderungen(az[i], nz[i])
            if blocks is None:
                ops.append((anfang, stelle, nz[i]))
            else:
                for b in reversed(blocks):
                    ops.append((anfang + b["von"], anfang + b["bis"], b["text"]))
            geaendert += 1
        stelle = anfang - 1
    return ops, False, geaendert
