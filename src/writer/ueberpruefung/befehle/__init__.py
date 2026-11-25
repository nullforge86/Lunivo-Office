"""Tür des Pakets ``writer.ueberpruefung.befehle``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "SCHUTZ_HINWEIS": ("befehle", "SCHUTZ_HINWEIS"),
    "aenderungen_befehle": ("befehle", "aenderungen_befehle"),
    "anzeige_befehle": ("befehle", "anzeige_befehle"),
    "ist_geschuetzt": ("befehle", "ist_geschuetzt"),
    "kommentare_befehle": ("befehle", "kommentare_befehle"),
    "markup_befehle": ("befehle", "markup_befehle"),
    "meldungen_an": ("befehle", "meldungen_an"),
    "noten_befehle": ("befehle", "noten_befehle"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "befehle":
        from . import befehle as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
