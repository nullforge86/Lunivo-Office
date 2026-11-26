"""Tür des Pakets ``writer.anbindung.zeichnen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "absaetze": ("anbindung", "absaetze"),
    "betonung": ("anbindung", "betonung"),
    "bild": ("anbindung", "bild"),
    "blase": ("anbindung", "blase"),
    "blasen_verbindung": ("anbindung", "blasen_verbindung"),
    "datei_symbol": ("anbindung", "datei_symbol"),
    "deckblatt": ("anbindung", "deckblatt"),
    "deckblatt_grafik": ("anbindung", "deckblatt_grafik"),
    "diagramm": ("anbindung", "diagramm"),
    "doppelt_durch": ("anbindung", "doppelt_durch"),
    "form": ("anbindung", "form"),
    "formel": ("anbindung", "formel"),
    "linie": ("anbindung", "linie"),
    "platzhalter": ("anbindung", "platzhalter"),
    "rahmen": ("anbindung", "rahmen"),
    "ruby": ("anbindung", "ruby"),
    "seitenrahmen": ("anbindung", "seitenrahmen"),
    "seitenrahmen_rechteck": ("anbindung", "seitenrahmen_rechteck"),
    "smartart_baum": ("anbindung", "smartart_baum"),
    "smartart_beginnen": ("anbindung", "smartart_beginnen"),
    "smartart_format_von": ("anbindung", "smartart_format_von"),
    "smartart_gruppen": ("anbindung", "smartart_gruppen"),
    "smartart_schrift": ("anbindung", "smartart_schrift"),
    "smartart_schrift_uebernehmen": ("anbindung", "smartart_schrift_uebernehmen"),
    "smartart_text": ("anbindung", "smartart_text"),
    "svg": ("anbindung", "svg"),
    "text_mit_effekt": ("anbindung", "text_mit_effekt"),
    "textfeld_bild": ("anbindung", "textfeld_bild"),
    "textfeld_blatt": ("anbindung", "textfeld_blatt"),
    "textfeld_farbe": ("anbindung", "textfeld_farbe"),
    "textfeld_freigeben": ("anbindung", "textfeld_freigeben"),
    "textfeld_hoehe": ("anbindung", "textfeld_hoehe"),
    "textfeld_passt": ("anbindung", "textfeld_passt"),
    "textfeld_setzen": ("anbindung", "textfeld_setzen"),
    "textfeld_zeilen": ("anbindung", "textfeld_zeilen"),
    "umschlossen": ("anbindung", "umschlossen"),
    "unterstrich": ("anbindung", "unterstrich"),
    "wasserzeichen": ("anbindung", "wasserzeichen"),
    "wordart": ("anbindung", "wordart"),
    "wordart_masse": ("anbindung", "wordart_masse"),
    "wordart_objekt": ("anbindung", "wordart_objekt"),
    "wordart_stil": ("anbindung", "wordart_stil"),
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
