"""Beschreibung der Bedienelemente rechts in der Statusleiste: die Dokumentansichten (Drucklayout, Gliederung, Lesemodus, Weblayout) und die Zeilen der
Zoom-Klappe. Nur Daten – die Knöpfe baut ``vcl/qt/widgets/statusleiste``, die Zuordnung zu den Befehlen steht in
``writer/werkzeugleisten/ansicht/aktionen/ansichtswahl_aktionen.py``."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Ansichtsart:
    """Eine Dokumentansicht der Statusleiste: Kennung für den Befehl, Name, Symbolname und Hinweistext."""
    kennung: str
    name: str
    symbol: str
    hinweis: str


@dataclass(frozen=True)
class Zoomwahl:
    """Eine Zeile der Zoom-Klappe: ``art`` ist ``wert`` (fester Prozentwert), ``breite`` (Seitenbreite), ``text`` (Textbreite) oder ``seite`` (ganze Seite)."""
    art: str
    text: str
    prozent: int = 0


ANSICHTSARTEN: tuple[Ansichtsart, ...] = (
    Ansichtsart("blatt", "Drucklayout", "blattansicht", "Drucklayout: das Dokument so, wie es gedruckt wird"),
    Ansichtsart("gliederung", "Gliederung", "gliederung", "Gliederung: nur die Überschriften des Dokuments"),
    Ansichtsart("lesen", "Lesemodus", "lesen", "Lesemodus: lesen ohne Bearbeiten (Strg+Umschalt+L)"),
    Ansichtsart("web", "Weblayout", "weblayout", "Weblayout: eine fortlaufende Seite in der Breite des Fensters"),
)

ZOOMWAHLEN: tuple[Zoomwahl, ...] = (
    Zoomwahl("wert", "200 %", 200),
    Zoomwahl("wert", "100 %", 100),
    Zoomwahl("wert", "75 %", 75),
    Zoomwahl("breite", "Seitenbreite"),
    Zoomwahl("text", "Textbreite"),
    Zoomwahl("seite", "Ganze Seite"),
)

ZOOM_PROZENT_MIN = 10       # kleinster und größter Zoom, den Regler und Prozentfeld anbieten
ZOOM_PROZENT_MAX = 500
