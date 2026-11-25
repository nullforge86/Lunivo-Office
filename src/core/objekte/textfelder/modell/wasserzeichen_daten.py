"""Wasserzeichen daten: aus ``vcl.qt.rendering.textfelder.wasserzeichen`` herausgelöst."""
from __future__ import annotations


VORGABEN = ("VERTRAULICH", "NICHT KOPIEREN", "ORIGINAL", "BEISPIEL", "STRENG GEHEIM", "EILT", "ENTWURF", "MUSTER", "KOPIE", "DRINGEND")


GROESSEN = (36, 40, 44, 48, 54, 60, 66, 72, 80, 90, 96, 105, 120, 144)


ZOOMS = (500, 200, 150, 100, 50)


HORIZONTAL = (("mitte", "Zentriert"), ("links", "Links"), ("rechts", "Rechts"))


VERTIKAL = (("mitte", "Zentriert"), ("oben", "Oben"), ("unten", "Unten"))


FORMATE = ((0, "Horizontal"), (-45, "Diagonal"))


STANDARD_FARBE = "#c0c0c0"


ALT_DECKKRAFT = 110 / 255                     # so sahen Wasserzeichen ohne Angabe „transparenz“ bisher aus


def da(w: dict | None) -> bool:
    """Ob das Wasserzeichen etwas zeigt (Text oder Bild)."""
    return bool(w and ((w.get("text") or "").strip() or w.get("bild")))
