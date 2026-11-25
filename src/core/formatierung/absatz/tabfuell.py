"""Füllzeichen vor Tabstopps (Punkte, Striche, Linie): Qt kennt sie nicht, Lunivo zeichnet sie selbst.

Im Absatzformat des Dokumentenmodells steht ``tabfuell`` (``"Position in px:Füllzeichen;…"``); gefüllt wird in der Layoutberechnung des Kerns. Hier stehen nur
die Arten für Fenster und DOCX.
"""
from __future__ import annotations

# Schlüssel → (Name im Fenster, Zeichen, DOCX-Wert)
FUELL = {"": ("1 Ohne", "", "none"), "punkt": ("2 .....", ".", "dot"), "strich": ("3 ----", "-", "hyphen"),
         "linie": ("4 ____", "_", "underscore"), "mitte": ("5 ······", "·", "middleDot")}


def aus_docx(wert: str | None) -> str:
    return next((k for k, v in FUELL.items() if k and v[2] == wert), "")
