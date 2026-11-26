"""Tür des Pakets ``framework.zeichnen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Farbe": ("zeichnungen", "Farbe"),
    "Flaeche": ("raster", "Flaeche"),
    "Rasterbild": ("raster", "Rasterbild"),
    "Rechteck": ("raster", "Rechteck"),
    "absaetze": ("textsatz", "absaetze"),
    "betonung": ("zeichnungen", "betonung"),
    "bild": ("zeichnungen", "bild"),
    "blase": ("zeichnungen", "blase"),
    "blasen_verbindung": ("zeichnungen", "blasen_verbindung"),
    "datei_symbol": ("einfuegen", "datei_symbol"),
    "deckblatt": ("zeichnungen", "deckblatt"),
    "deckblatt_grafik": ("zeichnungen", "deckblatt_grafik"),
    "diagramm": ("zeichnungen", "diagramm"),
    "doppelt_durch": ("zeichnungen", "doppelt_durch"),
    "form": ("einfuegen", "form"),
    "formel": ("einfuegen", "formel"),
    "linie": ("zeichnungen", "linie"),
    "platzhalter": ("zeichnungen", "platzhalter"),
    "rahmen": ("zeichnungen", "rahmen"),
    "ruby": ("zeichnungen", "ruby"),
    "seitenrahmen": ("zeichnungen", "seitenrahmen"),
    "seitenrahmen_rechteck": ("zeichnungen", "seitenrahmen_rechteck"),
    "smartart_baum": ("smartart", "smartart_baum"),
    "smartart_beginnen": ("smartart", "smartart_beginnen"),
    "smartart_format_von": ("smartart", "smartart_format_von"),
    "smartart_gruppen": ("smartart", "smartart_gruppen"),
    "smartart_schrift": ("smartart", "smartart_schrift"),
    "smartart_schrift_uebernehmen": ("smartart", "smartart_schrift_uebernehmen"),
    "smartart_text": ("smartart", "smartart_text"),
    "svg": ("zeichnungen", "svg"),
    "text_mit_effekt": ("zeichnungen", "text_mit_effekt"),
    "textfeld_bild": ("textsatz", "textfeld_bild"),
    "textfeld_blatt": ("textsatz", "textfeld_blatt"),
    "textfeld_farbe": ("textsatz", "textfeld_farbe"),
    "textfeld_freigeben": ("textsatz", "textfeld_freigeben"),
    "textfeld_hoehe": ("textsatz", "textfeld_hoehe"),
    "textfeld_passt": ("textsatz", "textfeld_passt"),
    "textfeld_setzen": ("textsatz", "textfeld_setzen"),
    "textfeld_zeilen": ("textsatz", "textfeld_zeilen"),
    "umschlossen": ("zeichnungen", "umschlossen"),
    "unterstrich": ("zeichnungen", "unterstrich"),
    "wasserzeichen": ("zeichnungen", "wasserzeichen"),
    "wordart": ("zeichnungen", "wordart"),
    "wordart_masse": ("zeichnungen", "wordart_masse"),
    "wordart_objekt": ("textsatz", "wordart_objekt"),
    "wordart_stil": ("einfuegen", "wordart_stil"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "einfuegen":
        from . import einfuegen as _datei
    elif datei == "raster":
        from . import raster as _datei
    elif datei == "smartart":
        from . import smartart as _datei
    elif datei == "textsatz":
        from . import textsatz as _datei
    elif datei == "zeichnungen":
        from . import zeichnungen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
