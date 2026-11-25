"""Tür des Pakets ``core.listen.mehrstufig``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "EBENEN": ("mehrstufig", "EBENEN"),
    "EXTRA": ("mehrstufig", "EXTRA"),
    "GLYPHEN": ("mehrstufig", "GLYPHEN"),
    "PLATZHALTER": ("mehrstufig", "PLATZHALTER"),
    "VORLAGEN": ("mehrstufig", "VORLAGEN"),
    "als_mehrstufig": ("mehrstufig", "als_mehrstufig"),
    "als_text": ("mehrstufig", "als_text"),
    "aufzaehlung": ("mehrstufig", "aufzaehlung"),
    "aus_block": ("mehrstufig", "aus_block"),
    "aus_text": ("mehrstufig", "aus_text"),
    "block_wert": ("mehrstufig", "block_wert"),
    "ebene": ("mehrstufig", "ebene"),
    "ebene_aus": ("mehrstufig", "ebene_aus"),
    "gliederung": ("mehrstufig", "gliederung"),
    "ist_aufzaehlung": ("mehrstufig", "ist_aufzaehlung"),
    "liste_als_text": ("mehrstufig", "liste_als_text"),
    "liste_aus_text": ("mehrstufig", "liste_aus_text"),
    "nummer_der_ebene": ("mehrstufig", "nummer_der_ebene"),
    "nummer_text": ("mehrstufig", "nummer_text"),
    "zaehlen": ("mehrstufig", "zaehlen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "mehrstufig":
        from . import mehrstufig as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
