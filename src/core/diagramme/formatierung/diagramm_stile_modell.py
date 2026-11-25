"""Diagramm stile modell: aus ``vcl.qt.rendering.diagramme.diagramm_stile`` herausgelöst."""
from __future__ import annotations


# Stile des Diagramms (Diagrammtools ▸ Diagrammstile): (Name, Grund, Schrift, Raster); die ersten vier behalten ihre Nummer
STILE = [("Standard", "#ffffff", "#3c4043", True), ("Ohne Raster", "#ffffff", "#3c4043", False),
         ("Hellgrau", "#f1f3f5", "#343a40", True), ("Dunkel", "#2b2d42", "#f1f3f5", True),
         ("Fetter Titel", "#ffffff", "#212529", True), ("Mit Datenbeschriftung", "#ffffff", "#3c4043", False),
         ("Mit Rahmen", "#ffffff", "#1f3864", True), ("Hellblau", "#e7f1fb", "#1c4f8c", True),
         ("Warm", "#fff4e6", "#7a3e00", True), ("Hellgrün", "#ebf7ee", "#1d4f28", False),
         ("Nachtblau", "#14213d", "#e5e5e5", True), ("Schwarz", "#000000", "#ffffff", False),
         ("Papier", "#fdf6e3", "#586e75", True), ("Hoher Kontrast", "#ffffff", "#000000", True)]


# Zusätze einzelner Stile: titel_pt/titel_fett (Titelschrift), labels (Datenbeschriftungen), rahmen (Farbe), raster_farbe
STIL_EXTRA = {4: {"titel_pt": 16, "titel_fett": True}, 5: {"labels": True}, 6: {"rahmen": "#1f3864"}, 7: {"raster_farbe": "#b9d4f5"},
              8: {"raster_farbe": "#ffd8a8"}, 10: {"raster_farbe": "#3a4a6b"}, 11: {"labels": True},
              12: {"rahmen": "#93a1a1", "raster_farbe": "#eee8d5"}, 13: {"titel_pt": 14, "titel_fett": True, "rahmen": "#000000", "raster_farbe": "#868e96"}}


def stile_liste() -> list[dict]:
    """Alle Formatvorlagen (Diagrammstile) für die Galerie: {nr, name, grund, schrift, raster, **Zusätze}."""
    return [{"nr": i, "name": n, "grund": g, "schrift": s, "raster": r, **STIL_EXTRA.get(i, {})} for i, (n, g, s, r) in enumerate(STILE)]
