"""Formen daten: aus ``vcl.qt.rendering.formen.formen`` herausgelöst."""
from __future__ import annotations
from core.formatierung.farben.farben import Farbe


STANDARD = {"fuell": Farbe.AKZENT_DUNKEL, "linie": "#1f3864", "strich": 2.0, "text": ""}


VORLAGEN = [("Blau", Farbe.AKZENT_DUNKEL, "#1f3864", 2.0), ("Grün", "#6bbf59", "#2d6a1f", 2.0), ("Orange", "#f4a259", "#9c4f0a", 2.0),
            ("Rot", "#e5645f", "#8c1d18", 2.0), ("Grau", "#ced4da", "#495057", 2.0), ("Nur Kontur", "", "#1f3864", 2.5),
            ("Dunkel", "#2b2d42", Farbe.SCHWARZ, 1.5), ("Hell mit dicker Kontur", "#fff3bf", "#e67700", 5.0)]


GRUPPEN_ABSTAND = 8


def form_daten(o: dict, breite: float, hoehe: float) -> dict:
    d = dict(STANDARD); d.update(o.get("daten", {}))
    d["breite"], d["hoehe"] = int(round(breite)), int(round(hoehe))
    return d


_FO_SCHLUESSEL = {"fuell": "form_fuell", "linie": "form_linie", "strich": "form_strich", "text": "text", "form": "form",
                  "breite": "breite", "hoehe": "hoehe"}


