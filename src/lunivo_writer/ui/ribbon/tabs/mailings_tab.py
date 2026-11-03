"""Reiter „Sendungen“ (nur nach „Register anpassen“ sichtbar): Serienbriefe. Die Formularfelder stehen nur im Reiter Einfügen (Gruppe Formulare)."""
from __future__ import annotations


def bauen(register: dict) -> dict:
    sen = dict(next(t for t in register["register"] if t["name"] == "Sendungen"))
    sen["gruppen"] = [dict(g) for g in sen["gruppen"] if g["name"] != "Formular"]
    return sen
