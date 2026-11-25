"""Tür des Pakets ``core.suche.textsuche``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ABSATZ": ("suche", "ABSATZ"),
    "ABSCHNITT": ("suche", "ABSCHNITT"),
    "END": ("suche", "END"),
    "FELD": ("suche", "FELD"),
    "FUSS": ("suche", "FUSS"),
    "GRAFIK": ("suche", "GRAFIK"),
    "GRENZE": ("suche", "GRENZE"),
    "MARKEN": ("suche", "MARKEN"),
    "SEITE": ("suche", "SEITE"),
    "SPALTE": ("suche", "SPALTE"),
    "SPEZIAL": ("suche", "SPEZIAL"),
    "SPEZIAL_ERSETZEN": ("suche", "SPEZIAL_ERSETZEN"),
    "SuchTeil": ("suche", "SuchTeil"),
    "Suchauftrag": ("suche", "Suchauftrag"),
    "ZEILE": ("suche", "ZEILE"),
    "ersatz_text": ("suche", "ersatz_text"),
    "gueltig": ("suche", "gueltig"),
    "muster": ("suche", "muster"),
    "naechster": ("suche", "naechster"),
    "offset_zu_position": ("suche", "offset_zu_position"),
    "position_zu_offset": ("suche", "position_zu_offset"),
    "roh_text": ("suche", "roh_text"),
    "treffer": ("suche", "treffer"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "suche":
        from . import suche as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
