"""Indexeinträge wie das Word-Feld XE: Haupt- und Untereintrag, Lesung, „Siehe …“, Seitenbereich über eine Textmarke, fette oder
kursive Seitenzahl. Keine Oberfläche.

Am markierten Text steht ``P_INDEX`` (Eintrag, „Haupt:Unter“) und, wenn etwas davon abweicht, ``P_INDEX_OPT`` (die Schalter als Text).

    e = Eintrag("Obst", "Apfel", siehe="Kernobst", fett=True)
    e.text()        → "Obst:Apfel"
    e.schalter()    → '\\t "Siehe Kernobst" \\b'
    feld(e)         → 'XE "Obst:Apfel" \\t "Siehe Kernobst" \\b'      (Feldanweisung fürs DOCX)
    aus_feld('XE "Obst:Apfel" \\b')  → Eintrag("Obst", "Apfel", fett=True)
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Eintrag:
    haupt: str
    unter: str = ""
    lesung: str = ""                 # Sortierschlüssel des Haupteintrags (Word \y)
    lesung_unter: str = ""           # Sortierschlüssel des Untereintrags
    siehe: str = ""                  # Querverweis statt Seitenzahl, z. B. „Kernobst“ → „Siehe Kernobst“
    marke: str = ""                  # Seitenbereich: Textmarke, deren Seiten genannt werden
    fett: bool = False
    kursiv: bool = False

    def text(self) -> str:
        return f"{self.haupt}:{self.unter}" if self.unter else self.haupt

    def schalter(self) -> str:
        teile = []
        if self.siehe:
            teile.append(f'\\t "Siehe {self.siehe}"')
        if self.marke:
            teile.append(f"\\r {self.marke}")
        if self.fett:
            teile.append("\\b")
        if self.kursiv:
            teile.append("\\i")
        if self.lesung or self.lesung_unter:
            teile.append(f'\\y "{self.lesung}:{self.lesung_unter}"' if self.lesung_unter else f'\\y "{self.lesung}"')
        return " ".join(teile)

    def sortierung(self) -> tuple[str, str]:
        return ((self.lesung or self.haupt).casefold(), (self.lesung_unter or self.unter).casefold())


def aus_text(text: str, schalter: str = "") -> Eintrag:
    """Eintrag aus ``P_INDEX`` und ``P_INDEX_OPT``."""
    haupt, _, unter = text.partition(":")
    e = Eintrag(haupt.strip(), unter.strip())
    teile = [t[1:-1] if t.startswith('"') else t for t in re.findall(r'\\\w|"[^"]*"|[^\s"]+', schalter)]
    i = 0
    while i < len(teile):
        s = teile[i].lower()
        wert = teile[i + 1] if i + 1 < len(teile) else ""
        if s == "\\t":
            e.siehe = re.sub(r"^\s*siehe\s+", "", wert, flags=re.I); i += 1
        elif s == "\\r":
            e.marke = wert; i += 1
        elif s == "\\y":
            e.lesung, _, e.lesung_unter = wert.partition(":"); i += 1
        elif s == "\\b":
            e.fett = True
        elif s == "\\i":
            e.kursiv = True
        i += 1
    return e


def feld(e: Eintrag) -> str:
    s = e.schalter()
    return f'XE "{e.text().replace(chr(34), chr(39))}"' + (f" {s}" if s else "")


def aus_feld(anweisung: str) -> Eintrag | None:
    """Eintrag aus einer Feldanweisung ``XE "…" …``; None, wenn es kein XE-Feld ist."""
    m = re.match(r'\s*XE\s+(?:"([^"]*)"|(\S+))(.*)$', anweisung, re.I | re.S)
    if not m:
        return None
    return aus_text(m.group(1) if m.group(1) is not None else m.group(2), m.group(3).strip())
