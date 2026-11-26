"""Tür des Pakets ``vcl.qt.rendering.smartart``: alle öffentlichen Namen des Pakets. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen (keine zusätzlichen Importzyklen). Gibt es einen Namen in
mehreren Dateien, heißt er hier ``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "aendern": ("smartart", "aendern"),
    "befehl_aufzaehlung": ("smartart", "befehl_aufzaehlung"),
    "befehl_form": ("smartart", "befehl_form"),
    "befehl_level": ("smartart", "befehl_level"),
    "befehl_verschieben": ("smartart", "befehl_verschieben"),
    "bild_rechtecke": ("smartart", "bild_rechtecke"),
    "bildfeld_bei": ("smartart", "bildfeld_bei"),
    "daten_der_auswahl": ("smartart", "daten_der_auswahl"),
    "einfuegen": ("smartart", "einfuegen"),
    "format_lesen": ("smartart", "format_lesen"),
    "format_setzen": ("smartart", "format_setzen"),
    "kann": ("smartart", "kann"),
    "knoten_bei": ("smartart", "knoten_bei"),
    "knoten_bild": ("smartart", "knoten_bild"),
    "knoten_bild_setzen": ("smartart", "knoten_bild_setzen"),
    "knoten_gewaehlt": ("smartart", "knoten_gewaehlt"),
    "knoten_rechtecke": ("smartart", "knoten_rechtecke"),
    "knoten_text": ("smartart", "knoten_text"),
    "knoten_text_setzen": ("smartart", "knoten_text_setzen"),
    "knoten_waehlen": ("smartart", "knoten_waehlen"),
    "knoten_zeilen": ("smartart", "knoten_zeilen"),
    "knoten_zeilen_setzen": ("smartart", "knoten_zeilen_setzen"),
    "punkt_rechtecke": ("smartart", "punkt_rechtecke"),
    "punktfeld_bei": ("smartart", "punktfeld_bei"),
    "zeichnen": ("smartart", "zeichnen"),
    "zeichnen_mit_knoten": ("smartart", "zeichnen_mit_knoten"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "smartart":
        from . import smartart as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
