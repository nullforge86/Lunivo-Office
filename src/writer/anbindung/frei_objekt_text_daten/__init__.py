"""Tür des Pakets ``writer.anbindung.frei_objekt_text_daten``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "arten": ("anbindung", "arten"),
    "form_standard": ("anbindung", "form_standard"),
    "gedreht": ("anbindung", "gedreht"),
    "laeufe_ab": ("anbindung", "laeufe_ab"),
    "laeufe_zusammen": ("anbindung", "laeufe_zusammen"),
    "ss": ("anbindung", "ss"),
    "standard_mass": ("anbindung", "standard_mass"),
    "text_arten": ("anbindung", "text_arten"),
    "textfeld_fuell": ("anbindung", "textfeld_fuell"),
    "textfeld_rand": ("anbindung", "textfeld_rand"),
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
