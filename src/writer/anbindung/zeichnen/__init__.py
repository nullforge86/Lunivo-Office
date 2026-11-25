"""Tür des Pakets ``writer.anbindung.zeichnen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "betonung": ("anbindung", "betonung"),
    "blase": ("anbindung", "blase"),
    "blasen_verbindung": ("anbindung", "blasen_verbindung"),
    "deckblatt": ("anbindung", "deckblatt"),
    "deckblatt_grafik": ("anbindung", "deckblatt_grafik"),
    "doppelt_durch": ("anbindung", "doppelt_durch"),
    "linie": ("anbindung", "linie"),
    "platzhalter": ("anbindung", "platzhalter"),
    "rahmen": ("anbindung", "rahmen"),
    "ruby": ("anbindung", "ruby"),
    "svg": ("anbindung", "svg"),
    "umschlossen": ("anbindung", "umschlossen"),
    "unterstrich": ("anbindung", "unterstrich"),
    "wasserzeichen": ("anbindung", "wasserzeichen"),
    "wordart": ("anbindung", "wordart"),
    "wordart_masse": ("anbindung", "wordart_masse"),
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
