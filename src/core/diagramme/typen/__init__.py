"""Tür des Pakets ``core.diagramme.typen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "FEHLER_ANTEIL": ("kartesisch", "FEHLER_ANTEIL"),
    "TABELLE_ZEILE": ("kartesisch", "TABELLE_ZEILE"),
    "dataclasses_ersetzen": ("kartesisch", "dataclasses_ersetzen"),
    "trend": ("kartesisch", "trend"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "kartesisch":
        from . import kartesisch as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
