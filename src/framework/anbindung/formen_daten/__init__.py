"""Tür des Pakets ``framework.anbindung.formen_daten``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "fo_schluessel": ("anbindung", "fo_schluessel"),
    "form_daten": ("anbindung", "form_daten"),
    "form_daten_setzen": ("anbindung", "form_daten_setzen"),
    "gruppen_abstand": ("anbindung", "gruppen_abstand"),
    "kette_glieder": ("anbindung", "kette_glieder"),
    "muster_an": ("anbindung", "muster_an"),
    "standard": ("anbindung", "standard"),
    "verknuepfbar": ("anbindung", "verknuepfbar"),
    "vorlagen": ("anbindung", "vorlagen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "anbindung":
        from . import anbindung as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
