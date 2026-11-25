"""Tür des Pakets ``framework.dokumentverwaltung.ausgabe``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "engine_setzen": ("textsatz", "engine_setzen"),
    "ist_emf": ("vektor_bilder", "ist_emf"),
    "ist_wmf": ("vektor_bilder", "ist_wmf"),
    "masse_px": ("vektor_bilder", "masse_px"),
    "metafile_rgba": ("vektor_bilder", "metafile_rgba"),
    "standard_engine": ("textsatz", "standard_engine"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "textsatz":
        from . import textsatz as _datei
    elif datei == "vektor_bilder":
        from . import vektor_bilder as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
