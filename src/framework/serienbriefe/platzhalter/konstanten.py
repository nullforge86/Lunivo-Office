"""Gemeinsame Werte der Sendungen: Farben der Seriendruckfelder und Regeln, das Feld „Nächster Datensatz“, die Form eines Feldes ``{{Name}}``.

Seriendruckfelder stehen als ``{{Name}}`` mit farbigem Hintergrund (``marker``) im Text, Regeln als Text mit dem Zeichenformat ``regel``
(„Feld|Wert|dann|sonst“)."""
from __future__ import annotations

import re

FELD_FARBE = "#d0ebff"
REGEL_FARBE = "#ffe8cc"
NAECHSTER = "Nächster Datensatz"
FELD = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")


def einzeilig(text: str) -> str:
    return " ".join(z.strip() for z in text.splitlines() if z.strip())
