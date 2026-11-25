"""Tür des Pakets ``writer.anbindung.mehrstufig``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "aufzaehlung": ("anbindung", "aufzaehlung"),
    "ebene_aus": ("anbindung", "ebene_aus"),
    "ebenen": ("anbindung", "ebenen"),
    "glyphen": ("anbindung", "glyphen"),
    "ist_aufzaehlung": ("anbindung", "ist_aufzaehlung"),
    "liste_als_text": ("anbindung", "liste_als_text"),
    "liste_aus_text": ("anbindung", "liste_aus_text"),
    "nummer_der_ebene": ("anbindung", "nummer_der_ebene"),
    "platzhalter": ("anbindung", "platzhalter"),
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
