"""Werte der Einstellungen: alles, was die JSON-Datei kennt (Wahrheitswerte, Zahlen, Zeichenketten, Listen, Wörterbücher oder nichts)."""
from __future__ import annotations

Wert = str | int | float | bool | list | dict | None
