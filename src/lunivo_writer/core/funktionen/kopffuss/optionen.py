"""Optionen der Kopf- und Fußzeile auf einer Seiteneinrichtung (``PageSettings``): erste Seite anders, gerade/ungerade Seiten, Verknüpfung mit dem
vorherigen Abschnitt, Leeren und Abstand zum Blattrand. Reine Fachlogik: die Funktionen ändern die übergebene Seiteneinrichtung."""
from __future__ import annotations

from lunivo_writer.core.dokument.seite import HeaderFooter, PageSettings

ALLE_FELDER = ("header", "footer", "first_header", "first_footer", "even_header", "even_footer")
WIRKSAMER_ABSTAND_MM = 8.0      # Lunivo zeichnet Kopf und Fuß fest 8 mm vom Blattrand, solange kein Abstand gesetzt ist
ABSTANDSFELDER = {"kopf": "kopf_abstand_mm", "fuss": "fuss_abstand_mm"}
VERKNUEPFUNGSFELDER = {"kopf": "kopf_verknuepft", "fuss": "fuss_verknuepft"}


def erste_seite_anders_umschalten(seite: PageSettings) -> None:
    seite.diff_first = not seite.diff_first
    if seite.diff_first and seite.first_header.is_empty() and seite.first_footer.is_empty():
        seite.first_header = HeaderFooter()
        seite.first_footer = HeaderFooter()


def gerade_ungerade_umschalten(seite: PageSettings) -> None:
    """Gerade Seiten bekommen eine eigene Kopf-/Fußzeile (zuerst eine Kopie der gewöhnlichen)."""
    seite.diff_even = not seite.diff_even
    if seite.diff_even and seite.even_header.is_empty() and seite.even_footer.is_empty():
        seite.even_header = seite.header.kopie()
        seite.even_footer = seite.footer.kopie()


def verknuepft(seite: PageSettings, was: str) -> bool:
    return bool(getattr(seite, VERKNUEPFUNGSFELDER[was]))


def verknuepfung_setzen(seite: PageSettings, was: str, an: bool) -> None:
    setattr(seite, VERKNUEPFUNGSFELDER[was], an)


def leeren(seite: PageSettings, felder: tuple[str, ...]) -> None:
    for f in felder:
        setattr(seite, f, getattr(seite, f).kopie(""))


def abstand_mm(seite: PageSettings, zone: str) -> float:
    """Der eingestellte Abstand, sonst der feste Abstand, den Lunivo zeichnet."""
    wert = float(getattr(seite, ABSTANDSFELDER[zone]) or 0.0)
    return wert if wert > 0 else WIRKSAMER_ABSTAND_MM


def abstand_setzen(seite: PageSettings, zone: str, mm: float) -> None:
    setattr(seite, ABSTANDSFELDER[zone], float(mm))
