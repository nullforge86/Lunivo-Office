"""Gestaltung des Diagramms: Stile (Grund, Schrift, Raster), Farbschemen und ihre Anwendung auf ein QtCharts-Diagramm. Keine Oberfläche."""
from __future__ import annotations

from PySide6.QtGui import QBrush, QColor, QPen

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


def _monochrom(basis: str) -> list[str]:
    """Sechs Töne einer Farbe, vom dunklen zum hellen."""
    c = QColor(basis)
    return [c.darker(f).name() for f in (170, 130)] + [c.name()] + [c.lighter(f).name() for f in (130, 165, 205)]


# Farbschemen (Diagrammstile ▸ Farben): Gruppe → [(Name, sechs Farben)]
FARBSCHEMEN = [
    ("Farbig", [("Farbig 1", ["#4a8fd8", "#ef8a3c", "#9aa0a6", "#f2b705", "#2f6fb5", "#5aa454"]),
                ("Farbig 2", ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6", "#e67e22"]),
                ("Farbig 3", ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51", "#8ab17d"]),
                ("Farbig 4", ["#6a4c93", "#1982c4", "#8ac926", "#ffca3a", "#ff595e", "#52a9a1"])]),
    ("Monochrom", [(f"Monochrom {i + 1}", _monochrom(c)) for i, c in
                   enumerate(["#4a8fd8", "#ef8a3c", "#868e96", "#f2b705", "#2f6fb5", "#5aa454", "#c0392b", "#7e57c2"])]),
]


def farbschemen_gruppen() -> list[tuple[str, list[tuple[str, list[str]]]]]:
    """Die Gruppen „Farbig“ und „Monochrom“ mit ihren Farbzeilen (Kopie von ``FARBSCHEMEN``)."""
    return [(g, [(n, list(f)) for n, f in z]) for g, z in FARBSCHEMEN]


def farbschemen_flach() -> list[tuple[str, list[str]]]:
    """Alle Farbzeilen hintereinander (Nummer = Argument von ``diagrammFarben``)."""
    return [(n, list(f)) for _g, z in FARBSCHEMEN for n, f in z]

SCHRIFT_STANDARD = "#3c4043"


def stil_schrift(stil: int) -> QColor:
    """Schriftfarbe des Stils (ungültige Nummer: Standardschrift)."""
    return QColor(STILE[stil][2] if 0 <= stil < len(STILE) else SCHRIFT_STANDARD)


def stil_grund(stil: int, kachel: bool = False) -> QColor:
    """Grundfarbe des Stils; Kacheln und ungültige Nummern sind weiß."""
    return QColor(STILE[stil][1] if 0 <= stil < len(STILE) and not kachel else "white")


def stil_anwenden(ch, stil: int, kachel: bool, gitter: bool = True) -> None:
    """Schrift- und Rasterfarben des Stils. Den Grund malt ``_bild`` selbst (das Diagramm liegt auf einer durchsichtigen Ebene)."""
    if kachel or not 0 <= stil < len(STILE):
        return
    _n, _grund, schrift, raster = STILE[stil]
    ex = STIL_EXTRA.get(stil, {})
    ch.setBackgroundVisible(False)
    ch.setTitleBrush(QBrush(QColor(schrift)))
    if ex.get("titel_pt"):
        f = ch.titleFont(); f.setPointSizeF(ex["titel_pt"]); f.setBold(bool(ex.get("titel_fett"))); ch.setTitleFont(f)
    ch.legend().setLabelColor(QColor(schrift))
    for achse in ch.axes():
        achse.setGridLineVisible(raster and gitter)
        achse.setLabelsColor(QColor(schrift))
        if ex.get("raster_farbe"):
            achse.setGridLinePen(QPen(QColor(ex["raster_farbe"]), 1))
        if hasattr(achse, "setLinePenColor"):
            achse.setLinePenColor(QColor(schrift))
