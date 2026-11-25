"""Tür des Pakets ``framework.zeichnen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Farbe": ("zeichnungen", "Farbe"),
    "Flaeche": ("raster", "Flaeche"),
    "Rasterbild": ("raster", "Rasterbild"),
    "Rechteck": ("raster", "Rechteck"),
    "betonung": ("zeichnungen", "betonung"),
    "blase": ("zeichnungen", "blase"),
    "blasen_verbindung": ("zeichnungen", "blasen_verbindung"),
    "deckblatt": ("zeichnungen", "deckblatt"),
    "deckblatt_grafik": ("zeichnungen", "deckblatt_grafik"),
    "doppelt_durch": ("zeichnungen", "doppelt_durch"),
    "linie": ("zeichnungen", "linie"),
    "platzhalter": ("zeichnungen", "platzhalter"),
    "rahmen": ("zeichnungen", "rahmen"),
    "ruby": ("zeichnungen", "ruby"),
    "svg": ("zeichnungen", "svg"),
    "umschlossen": ("zeichnungen", "umschlossen"),
    "unterstrich": ("zeichnungen", "unterstrich"),
    "wasserzeichen": ("zeichnungen", "wasserzeichen"),
    "wordart": ("zeichnungen", "wordart"),
    "wordart_masse": ("zeichnungen", "wordart_masse"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "raster":
        from . import raster as _datei
    elif datei == "zeichnungen":
        from . import zeichnungen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
