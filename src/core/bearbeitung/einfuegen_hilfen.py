"""Einfuegen hilfen: aus ``vcl.qt.rendering.formen.einfuegen`` herausgelöst."""
from __future__ import annotations


# Galerie „Formatvorlage“ (Einfügen ▸ WordArt ▾): 15 eigene Stile, angelehnt an die Vorlage (Neun oben, sechs darunter).
# (Name, Füllung oben, Füllung unten oder None = nur Kontur, Kontur oder None, Konturbreite, Schatten oder None)
WORDART_VORLAGEN = [
    ("Schwarz mit Schatten", "#111111", "#111111", None, 0, "#9aa0a6"),
    ("Blau, Verlauf", "#8fc1ec", "#2f78bd", None, 0, None),
    ("Orange, Verlauf", "#f6a96a", "#d9601a", None, 0, None),
    ("Blaue Kontur", "#ffffff", "#ffffff", "#4f93d1", 2.0, None),
    ("Gold", "#ffc933", "#f0a500", None, 0, None),
    ("Grau", "#9a9a9a", "#7c7c7c", None, 0, None),
    ("Dunkelblau, Verlauf", "#5b86d6", "#1f3f8f", None, 0, "#b8c4dc"),
    ("Gelb mit heller Kontur", "#ffe27a", "#ffd23f", "#fff3c4", 1.6, None),
    ("Hellblaue Kontur", "#ffffff", "#e8f1fb", "#9cc3ea", 2.0, None),
    ("Grau mit Schatten", "#8a8a8a", "#6e6e6e", None, 0, "#2b2b2b"),
    ("Schwarz, blauer Rand", "#141414", "#141414", "#5b86d6", 1.6, "#b8c4dc"),
    ("Dunkle Kontur, blauer Schatten", "#ffffff", "#eef2f8", "#1f2d4d", 2.0, "#5b86d6"),
    ("Blau mit heller Kontur", "#3b7fcf", "#2461a8", "#b9d6f2", 1.8, None),
    ("Orange Kontur", "#ffffff", "#fdeadb", "#e8803a", 2.0, "#f4c9a5"),
    ("Hellgrau, verblasst", "#e6e6e6", "#c4c4c4", "#d9d9d9", 1.2, None),
]
