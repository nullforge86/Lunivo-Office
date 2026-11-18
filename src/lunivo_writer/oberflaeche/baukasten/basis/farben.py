"""Farbdaten für jede Palette im Programm: Themenfarben mit Abstufungen, Standardfarben, zuletzt benutzte."""
from __future__ import annotations

from PySide6.QtCore import QSettings
from PySide6.QtGui import QColor

# Eigene Grundfarben (Weiß, Schwarz, zwei Grautöne, dann die Farben der Oberfläche) — jede Spalte bekommt fünf Abstufungen.
THEMA_FARBEN = ("#ffffff", "#000000", "#e9ecef", "#343a40", "#1971c2", "#e8590c", "#868e96", "#f08c00", "#1098ad", "#2f9e44")
STANDARD_FARBEN = ("#c92a2a", "#f03e3e", "#f08c00", "#ffd43b", "#82c91e", "#2f9e44", "#1098ad", "#1971c2", "#364fc7", "#6741d9")
# Voreinstellungsfarben für Benutzerobjekte und Dokumentdaten (werden bewusst nicht thematisiert).
VORGABE_WASSERZEICHEN = "#c0c0c0"      # Standardfarbe der Wasserzeichen
VORGABE_WORDART = "#2f78bd"            # Standardfarbe eines WordArt-Objekts im Dialog
VORGABE_MARKER = "#ffec99"             # Standardfarbe des Textmarkers
VORGABE_SCHATTIERUNG = "#d9d9d9"       # Zeichenschattierung
VORGABE_LINIE = "#1f3864"             # Standard-Linienfarbe einer neuen Form im Dialog
VORGABE_SCHRIFT = "#1f2328"            # Standard-Schriftfarbe eines neuen Textobjekts im Dialog
VORGABE_TABELLENRAND = "#333333"       # Rand einer per Befehl umrandeten Tabelle
# Heller Kachelgrund für Vorschauen mit dunkler Schrift (in allen Themen gleich hell, damit auch das schwarze „A“ zu sehen ist).
KACHEL_GRUND = "#f3f4f6"
KACHEL_RAND = "#d0d4d9"
ZULETZT_SCHLUESSEL = "baukasten/zuletzt_farben"
ZULETZT_MAX = 10


def mische(a: str, b: str, anteil: float) -> str:
    """Mischt Farbe a zum Anteil (0…1) mit Farbe b."""
    x, y = QColor(a), QColor(b)
    return QColor(round(x.red() + (y.red() - x.red()) * anteil), round(x.green() + (y.green() - x.green()) * anteil),
                  round(x.blue() + (y.blue() - x.blue()) * anteil)).name()


def abstufungen(farbe: str) -> list[str]:
    """Fünf Abstufungen einer Themenfarbe, von hell nach dunkel (Weiß geht nur nach Grau, Schwarz nur nach Grau)."""
    f = QColor(farbe).name()
    if f == "#ffffff":
        return [mische(f, "#000000", t) for t in (0.05, 0.15, 0.25, 0.35, 0.5)]
    if f == "#000000":
        return [mische(f, "#ffffff", t) for t in (0.5, 0.35, 0.25, 0.15, 0.05)]
    return [mische(f, "#ffffff", 0.8), mische(f, "#ffffff", 0.6), mische(f, "#ffffff", 0.4),
            mische(f, "#000000", 0.25), mische(f, "#000000", 0.5)]


def thema_raster() -> list[list[str]]:
    """Zeilen der Themenfarben: erst die Grundfarben, darunter die fünf Abstufungen."""
    spalten = [[f] + abstufungen(f) for f in THEMA_FARBEN]
    return [[s[z] for s in spalten] for z in range(6)]


def zuletzt_laden() -> list[str]:
    try:
        wert = QSettings().value(ZULETZT_SCHLUESSEL, [])
    except Exception:
        return []
    if isinstance(wert, str):
        wert = [wert] if wert else []
    return [QColor(w).name() for w in (wert or []) if QColor(w).isValid()][:ZULETZT_MAX]


def zuletzt_merken(farbe: str) -> None:
    f = QColor(farbe).name()
    liste = [f] + [x for x in zuletzt_laden() if x != f]
    try:
        QSettings().setValue(ZULETZT_SCHLUESSEL, liste[:ZULETZT_MAX])
    except Exception:
        pass
