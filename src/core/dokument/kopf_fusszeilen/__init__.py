"""Tür des Pakets ``core.dokument.kopf_fusszeilen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ABSTANDSFELDER": ("optionen", "ABSTANDSFELDER"),
    "ALLE_FELDER": ("optionen", "ALLE_FELDER"),
    "DOCX_FORMAT": ("seitenzahl", "DOCX_FORMAT"),
    "MUSTER": ("seitenzahl", "MUSTER"),
    "POSITIONEN": ("seitenzahl", "POSITIONEN"),
    "TRENNER": ("seitenzahl", "TRENNER"),
    "VERKNUEPFUNGSFELDER": ("optionen", "VERKNUEPFUNGSFELDER"),
    "VORGABEN": ("seitenzahl", "VORGABEN"),
    "WIRKSAMER_ABSTAND_MM": ("optionen", "WIRKSAMER_ABSTAND_MM"),
    "absatz_oben": ("seitenzahl", "absatz_oben"),
    "abstand_mm": ("optionen", "abstand_mm"),
    "abstand_setzen": ("optionen", "abstand_setzen"),
    "ausrichtung": ("seitenzahl", "ausrichtung"),
    "erste_nummer": ("seitenzahl", "erste_nummer"),
    "erste_seite_anders_umschalten": ("optionen", "erste_seite_anders_umschalten"),
    "gerade_ungerade_umschalten": ("optionen", "gerade_ungerade_umschalten"),
    "leeren": ("optionen", "leeren"),
    "nummer": ("seitenzahl", "nummer"),
    "seitenwechsel": ("seitenzahl", "seitenwechsel"),
    "seitenzahl_loeschen_bereich": ("seitenzahl", "seitenzahl_loeschen_bereich"),
    "seitenzahl_setzen": ("seitenzahl", "seitenzahl_setzen"),
    "seitenzahlen_entfernen": ("seitenzahl", "seitenzahlen_entfernen"),
    "text": ("seitenzahl", "text"),
    "verknuepft": ("optionen", "verknuepft"),
    "verknuepfung_setzen": ("optionen", "verknuepfung_setzen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "optionen":
        from . import optionen as _datei
    elif datei == "seitenzahl":
        from . import seitenzahl as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
