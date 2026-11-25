"""Aufzählungen und Nummerierungen: die Arten, die Lunivo zeichnet und in DOCX schreibt, und ihre Beschreibung als kleines Wörterbuch.

Eine Liste ist ``{"stil": Schlüssel aus STILE, "praefix": "", "suffix": ".", "start": 1}`` (Aufzählungen: nur ``stil``).
Eine Nummerierung kann ``"zeichen"`` tragen (Schrift, Fett, Kursiv, Größe, Farbe der Nummern, Werte wie in ``text_format.ZEICHEN``).
Als Text (für eine Formatvorlage) steht sie als ``stil|praefix|suffix|start|zeichen als JSON``; ein leerer Text heißt: keine Liste.
"""
from __future__ import annotations

import json

# Schlüssel → (Name, Aufzählung?, Schlüssel der Listenart im Dokumentenmodell, Ziffernfolge für Vorschau und Zahlenformat)
STILE = {
    "disc": ("Punkt", True, "disc", ""),
    "circle": ("Kreis", True, "circle", ""),
    "square": ("Quadrat", True, "square", ""),
    "dezimal": ("1, 2, 3, …", False, "dezimal", "1|2|3"),
    "klein": ("a, b, c, …", False, "klein", "a|b|c"),
    "gross": ("A, B, C, …", False, "gross", "A|B|C"),
    "roem_klein": ("i, ii, iii, …", False, "roem_klein", "i|ii|iii"),
    "roem_gross": ("I, II, III, …", False, "roem_gross", "I|II|III"),
}
AUFZAEHLUNGEN = tuple(k for k, v in STILE.items() if v[1])
# Nummerierungen der Auswahl (Reiter „Nummerierung“): (Stil, Präfix, Suffix)
NUMMERIERUNGEN = (("dezimal", "", "."), ("dezimal", "", ")"), ("roem_gross", "", "."), ("gross", "", "."),
                  ("klein", "", ")"), ("klein", "", "."), ("roem_klein", "", "."))


ZEICHEN_FELDER = ("schrift", "fett", "kursiv", "groesse", "farbe")


def zeichen_filtern(w: dict | None) -> dict:
    """Aus den Werten eines Schriftart-Fensters nur das, was für Nummern gilt und gesetzt ist."""
    return {k: w[k] for k in ZEICHEN_FELDER if w and w.get(k)}


def liste(stil: str, praefix: str = "", suffix: str = ".", start: int = 1, zeichen: dict | None = None, pos: dict | None = None) -> dict:
    """``pos``: eigene Position der Nummer (``ausr``, ``ausr_art``, ``tab``, ``einzug`` in mm) — dann zeichnet Lunivo die Nummer selbst."""
    if STILE[stil][1]:
        return {"stil": stil, "praefix": "", "suffix": "", "start": 1}
    d = {"stil": stil, "praefix": praefix, "suffix": suffix, "start": max(1, int(start))}
    z = zeichen_filtern(zeichen)
    if z:
        d["zeichen"] = z
    if pos:
        d["pos"] = {k: pos[k] for k in ("ausr", "ausr_art", "tab", "einzug", "danach") if k in pos}
    return d


def marke(spec: dict) -> str | None:
    """Zeichenfolge für ``liste_zeichner`` (Vorschaubild) dieser Liste."""
    st = STILE[spec["stil"]]
    if st[1]:
        return spec["stil"]
    return "|".join(spec["praefix"] + z + spec["suffix"] for z in st[3].split("|"))
