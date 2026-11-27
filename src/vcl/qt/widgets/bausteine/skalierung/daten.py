"""Datenschicht der Oberfläche — die unterste Stufe: Inhalte stehen in ``ressourcen/daten/*.json``, nicht im Code.

``lade("datei_ansicht")`` liest die Datei einmal und gibt das Ergebnis zurück (leeres Wörterbuch, wenn sie fehlt oder defekt ist).
Bausteine darüber (Gerüst, Seiten) bekommen ihre Beschriftungen, Reihenfolgen und Symbolnamen von hier."""
from __future__ import annotations

import json
import os

from system import pfade

_ZWISCHENSPEICHER: dict[str, dict] = {}


def lade(name: str) -> dict:
    if name not in _ZWISCHENSPEICHER:
        try:
            with open(os.path.join(pfade.RESSOURCEN, "daten", f"{name}.json"), encoding="utf-8") as fh:
                _ZWISCHENSPEICHER[name] = json.load(fh)
        except (OSError, ValueError):
            _ZWISCHENSPEICHER[name] = {}
    return _ZWISCHENSPEICHER[name]


def text(stichwort: str) -> str:
    """Der Text zu einem Stichwort aus ``ressourcen/daten/texte.json``. Fehlt das Stichwort, erscheint es selbst — so fällt eine Lücke sofort auf."""
    return lade("texte").get(stichwort, stichwort)
