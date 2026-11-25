"""Sprechblasen (Kommentare und Änderungen im Seitenrand): unveränderliche Datentypen, die das Framework der Oberfläche übergibt."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Sprechblase:
    """Eine Blase: die Stelle im Rohtext (``von`` bis ``bis``), Autor, Datum, Art („kommentar“ | „ins“ | „del“), Text, Farbe und Kommentar-Id."""
    von: int
    bis: int
    autor: str
    datum: str
    art: str
    text: str
    farbe: str
    kid: int | None = None


@dataclass(frozen=True)
class BlasenSchrift:
    """Die Schrift der Blasen: Familie, Größe in Punkt, Gewicht (400 normal, 700 fett) und Kursiv."""
    familie: str
    groesse_pt: float
    gewicht: int = 400
    kursiv: bool = False


@dataclass(frozen=True)
class BlasenEinstellung:
    """Die Einstellungen der Sprechblasen (Optionen ▸ Befehle)."""
    verwenden: str
    breite_mm: float
    empfohlen: bool
    rand: str
    linien: bool
    ausrichtung: str


@dataclass(frozen=True)
class BlasenKatalog:
    """Auswahlmöglichkeiten, Standardwerte und Maße der Sprechblasen."""
    verwenden: tuple[str, ...]
    rand: tuple[str, ...]
    ausrichtung: tuple[str, ...]
    standard: BlasenEinstellung
    luecke_mm: float
    kopf_hoehe: float
    blase_rand: float
    blase_ueberabtastung: float
