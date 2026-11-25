"""Qt-freie Fachlogik für den Text eines Querverweises (Seitenzahl, Nummer, Text, oben/unten)."""
from __future__ import annotations


def querverweis_text_bilden(ziel: dict, wie: str, cursor_position: int,
                            seitenzahl=None, oben_unten: bool = False) -> str:
    richtung = "oben" if ziel["pos"] < cursor_position else "unten"
    if wie == "obenunten":
        return richtung
    if wie == "seite":
        text = str(seitenzahl)
    elif wie == "nummer":
        text = ziel.get("nummer") or ziel["text"]
    elif wie == "nur_text":
        text = ziel.get("inhalt", ziel["text"])
    else:
        text = (ziel.get("inhalt", ziel["text"])
                if ziel["art"] in ("Textmarke", "Nummeriertes Element")
                else ziel["text"])
    if oben_unten and wie in ("seite", "nummer"):
        text += " " + richtung
    return text
