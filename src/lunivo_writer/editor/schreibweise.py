"""Groß-/Kleinschreibung und Sortierreihenfolge als reine Textfunktionen (ohne Oberfläche, einzeln testbar)."""
from __future__ import annotations

import re

# Schlüssel und Text im Fenster „Groß-/Kleinschreibung“ — in der Reihenfolge und mit den Worten der Vorlage
SCHREIBWEISEN = (("satz", "Ersten Buchstaben im Satz groß schreiben"), ("lower", "Kleinbuchstaben"), ("upper", "Großbuchstaben"),
                 ("toggle", "gROSS-/kLEINSCHREIBUNG umkehren"), ("title", "Erster Buchstabe groß"))


def umwandeln(text: str, art: str) -> str:
    if art == "upper":
        return text.upper()
    if art == "lower":
        return text.lower()
    if art == "title":
        return re.sub(r"[^\W\d_]+(?:['’][^\W\d_]+)?", lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), text)
    if art == "toggle":
        return text.swapcase()
    if art == "satz":
        return re.sub(r"(^\s*|[.!?…]\s+)([^\W\d_])", lambda m: m.group(1) + m.group(2).upper(), text.lower())
    raise ValueError(art)


def sortiert(texte: list[str], *, absteigend: bool = False, typ: str = "text", gross_klein: bool = False) -> list[str]:
    """Die Texte in der gewünschten Reihenfolge. ``typ``: ``text``, ``zahl`` (erste Zahl im Text) oder ``datum`` (TT.MM.JJJJ)."""
    def zahl(t: str) -> float:
        m = re.search(r"-?\d+(?:[.,]\d+)?", t.replace(" ", ""))
        return float(m.group(0).replace(",", ".")) if m else float("-inf")

    def datum(t: str) -> tuple:
        m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})", t)
        return (int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else (0, 0, 0)

    schluessel = {"zahl": zahl, "datum": datum}.get(typ) or (lambda t: t if gross_klein else t.casefold())
    return sorted(texte, key=schluessel, reverse=absteigend)
