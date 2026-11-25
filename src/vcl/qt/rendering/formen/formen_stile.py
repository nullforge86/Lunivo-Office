from __future__ import annotations
import copy
from PySide6.QtGui import QColor
from vcl.qt.rendering.formen import bildeffekte as BE
from core.objekte.formen.formen_stile_daten import SPALTEN, ZEILEN


def formstil(zeile: int, spalte: int) -> dict:
    """Die Werte des Stils: {"fuell": Farbe oder "" (keine), "fuell_art": "" | verlauf | abgestuft | glanz, "linie": Farbe, "strich": pt,
    "effekt": Wörterbuch für ``fx`` oder None}."""
    zeile = max(0, min(zeile, len(ZEILEN) - 1)); spalte = max(0, min(spalte, len(SPALTEN) - 1))
    farbe = SPALTEN[spalte][1]
    dunkel = QColor(farbe).darker(150).name()
    if zeile == 0:
        return {"fuell": "", "fuell_art": "", "linie": farbe, "strich": 2.5, "effekt": None}
    if zeile == 1:
        return {"fuell": farbe, "fuell_art": "", "linie": dunkel, "strich": 1.5, "effekt": None}
    if zeile == 2:
        return {"fuell": farbe, "fuell_art": "verlauf", "linie": dunkel, "strich": 1.5, "effekt": None}
    if zeile == 3:
        return {"fuell": farbe, "fuell_art": "abgestuft", "linie": dunkel, "strich": 1.5, "effekt": None}
    if zeile == 4:
        return {"fuell": farbe, "fuell_art": "glanz", "linie": dunkel, "strich": 1.5, "effekt": None}
    d3 = copy.deepcopy(BE.VORGABE["d3"]); d3["tiefe"] = 8.0; d3["tiefe_farbe"] = dunkel
    return {"fuell": farbe, "fuell_art": "verlauf", "linie": dunkel, "strich": 1.0, "effekt": {"d3": d3}}


def formstile_raster() -> list[list[dict]]:
    """Das Raster für die Galerie: [Zeile][Spalte] = {"zeile", "spalte", "name" (z. B. „Voll – Blau“), **Werte von ``formstil``}."""
    return [[{"zeile": z, "spalte": s, "name": f"{ZEILEN[z]} – {SPALTEN[s][0]}", **formstil(z, s)} for s in range(len(SPALTEN))]
            for z in range(len(ZEILEN))]
