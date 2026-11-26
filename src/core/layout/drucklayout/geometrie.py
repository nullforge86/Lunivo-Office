"""Maße und Kleinteile des Seitenlayouts: Blattabstand, Zellenpolster, Notenmaße, Mindestgrößen; die Gitterstelle einer Tabellenzelle."""
from __future__ import annotations

from dataclasses import dataclass
from core.layout.drucklayout.ergebnis import Platz, Seite

BLATT_ABSTAND_PX = 32.0               # grauer Zwischenraum zwischen zwei Blättern bei 100 % Zoom
ZELLEN_POLSTER = 4.0                  # Abstand zwischen Zelle und Inhalt
ZELLEN_ZWISCHENRAUM = 0.0             # Standard: zusammenhängendes Gitter, Nachbarzellen teilen sich die Linie; Abstand nur über ``zellabstand``
FREIE_TABELLE_ABSTAND = 8.0           # Abstand zwischen einer frei platzierten Tabelle und dem Text, der um sie läuft
UMFLUSS_MINDESTBREITE = 72.0          # bleibt neben einer frei platzierten Tabelle weniger Platz, läuft der Text nur darüber und darunter
STANDARD_OBJEKT =(64.0, 64.0)
NOTEN_ABSTAND = 3.0                   # px zwischen zwei Fußnoten
NOTEN_TRENNER = 12.0                  # px für den Trennstrich über den Fußnoten
NOTEN_SCHRIFT = 0.85                  # Fußnotenschrift im Verhältnis zur Grundschrift
NOTEN_SEITENANTEIL = 0.85             # füllen die Fußnoten mehr als diesen Teil der Seite, läuft der Rest über
NOTEN_LINIE_ANTEIL = 1 / 3            # Länge des Trennstrichs im Verhältnis zur Spaltenbreite
MIN_TEILHOEHE = 40.0                  # weniger Platz als das bleibt: eine zu hohe Tabellenzeile beginnt erst auf der nächsten Seite
MIN_TABELLENBREITE = 20.0
MIN_SPALTENBREITE = 10.0
WEB_RAND = 24.0                       # Rand um den Text im Weblayout
FORTLAUFEND, GERADE, UNGERADE = "fortlaufend", "gerade", "ungerade"


@dataclass
class _Z:
    """Eine sichtbare Tabellenzelle an ihrer Gitterstelle."""
    z: int
    s: int
    zelle: object
