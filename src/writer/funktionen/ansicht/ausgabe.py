"""Ausgabe eines Dokuments für Druck, Druckvorschau und Bildexport: Das Framework setzt das Dokument und hält die Ausgabe unter einer Nummer;
die Oberfläche fragt Seitenzahl, Maße und fertige Seitenbilder ab."""
from __future__ import annotations

from framework.befehle import ansicht as _fw


def ausgabe_oeffnen(kennung: int, nur_formular: bool = False, versteckt: bool = False, blasen=None) -> int:
    """Das Dokument ``kennung`` für die Ausgabe setzen; → Nummer der Ausgabe (``blasen``: ``BlasenEinstellung`` vom Framework oder ``None``)."""
    return _fw.ausgabe_oeffnen(kennung, bool(nur_formular), bool(versteckt), blasen)


def ausgabe_aus_geruest(zeilen: list[str], benutzer: dict, heute: str) -> int:
    """Die Ausgabe eines neuen Dokuments mit dem Gerüst einer Dokumentvorlage; → Nummer der Ausgabe."""
    return _fw.ausgabe_aus_geruest(zeilen, benutzer, heute)


def ausgabe_aus_datei(pfad: str) -> int:
    """Die Ausgabe einer Datei (für das Vorschaubild einer Vorlage); → Nummer der Ausgabe."""
    return _fw.ausgabe_aus_datei(pfad)


def ausgabe_schliessen(nummer: int) -> None:
    _fw.ausgabe_schliessen(nummer)


def ausgabe_anzahl(nummer: int) -> int:
    return _fw.ausgabe_anzahl(nummer)


def ausgabe_seite_mm(nummer: int, index: int) -> tuple[float, float]:
    """Breite und Höhe der Seite ``index`` (ab 0) in Millimetern."""
    return _fw.ausgabe_seite_mm(nummer, index)


def ausgabe_blasen(nummer: int, index: int) -> list:
    """[(Blase, y der Textstelle auf dem Blatt)] der Sprechblasen neben der Seite ``index``."""
    return list(_fw.ausgabe_blasen(nummer, index))


def ausgabe_seitenbild(nummer: int, index: int, faktor: float, wasserzeichen: str = "", wasserzeichen_farbe: str = "") -> tuple[int, int, bytes]:
    """Die Seite ``index`` in der Auflösung ``faktor`` als ``(Breite, Höhe, RGBA)``; ``wasserzeichen``: Text schräg und blass über der Seite."""
    return _fw.ausgabe_seitenbild(nummer, index, faktor, wasserzeichen, wasserzeichen_farbe)


def ausgabe_als_pdf(nummer: int, ziel: str, seiten: list[int]) -> int:
    """Die Seiten ``seiten`` (ab 1) als Vektor-PDF nach ``ziel`` schreiben; → Zahl der geschriebenen Seiten."""
    return _fw.ausgabe_als_pdf(nummer, ziel, seiten)
