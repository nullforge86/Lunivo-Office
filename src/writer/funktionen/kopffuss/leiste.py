"""Die Knöpfe, die beim Bearbeiten von Kopf- und Fußzeile auf dem Blatt liegen, als Beschreibung: Schlüssel, Beschriftung, Symbol und wann sie
erscheinen. Die Oberfläche baut daraus die Leiste neben dem Etikett und das Absatz-Symbol; was ein Knopf tut, steht in ``klappen.py``."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BlattKnopf:
    """``mit_seitenzahl``: der Knopf erscheint, wenn die Zeile eine Seitenzahl trägt (``True``) oder wenn sie keine trägt (``False``)."""
    schluessel: str
    text: str
    symbol: str
    mit_seitenzahl: bool = True
    hinweis: str = ""


LEISTE = (
    BlattKnopf("neu", "Seitenzahl neu aufbauen", "file-plus"),
    BlattKnopf("format", "Seitenzahlenformat", "file-text"),
    BlattKnopf("loeschen", "Seitenzahl löschen", "x"),
    BlattKnopf("einfuegen", "Seitenzahl einfügen", "file-plus", mit_seitenzahl=False),
)
ABSATZ = BlattKnopf("absatz", "", "pilcrow", hinweis="Absatz")
