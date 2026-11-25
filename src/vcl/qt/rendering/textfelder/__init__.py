"""Tür des Pakets ``vcl.qt.rendering.textfelder``: alle öffentlichen Namen des Pakets. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen (keine zusätzlichen Importzyklen). Gibt es einen Namen in
mehreren Dateien, heißt er hier ``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "BEREICHE": ("felder", "BEREICHE"),
    "DATUMSFORMATE": ("felder", "DATUMSFORMATE"),
    "FELDER": ("felder", "FELDER"),
    "FUNKTIONEN": ("felder", "FUNKTIONEN"),
    "MERGEFORMAT": ("felder", "MERGEFORMAT"),
    "SCHREIBWEISEN": ("felder", "SCHREIBWEISEN"),
    "SEQ_KATEGORIEN": ("felder", "SEQ_KATEGORIEN"),
    "ZAHLENFORMATE": ("felder", "ZAHLENFORMATE"),
    "alle_zuruecksetzen": ("formular", "alle_zuruecksetzen"),
    "bild_aus_text": ("wasserzeichen", "bild_aus_text"),
    "bild_zu_text": ("wasserzeichen", "bild_zu_text"),
    "deckblatt_einfuegen": ("deckblatt", "einfuegen"),
    "deckblatt_zeichnen": ("deckblatt", "zeichnen"),
    "effekte_auf_text": ("frei_objekt_text", "effekte_auf_text"),
    "eingabe_anbieter": ("formular", "eingabe_anbieter"),
    "ergebnis": ("felder", "ergebnis"),
    "feld_einfuegen": ("felder", "feld_einfuegen"),
    "formel": ("felder", "formel"),
    "formel_bild": ("formel_einfuegen", "formel_bild"),
    "formel_einfuegen_formel_einfuegen": ("formel_einfuegen", "formel_einfuegen"),
    "formel_teile": ("formel_einfuegen", "formel_teile"),
    "formular_einfuegen": ("formular", "einfuegen"),
    "grafik_bild": ("deckblatt", "grafik_bild"),
    "klick": ("formular", "klick"),
    "kontext_sammeln": ("felder", "kontext_sammeln"),
    "nur_formulardaten": ("formular", "nur_formulardaten"),
    "richtung_anwenden": ("frei_objekt_text", "richtung_anwenden"),
    "schreibweise": ("felder", "schreibweise"),
    "tabellen_bereiche": ("felder", "tabellen_bereiche"),
    "textfeld_zeichnen": ("frei_objekt_text", "textfeld_zeichnen"),
    "vorgabe": ("felder", "vorgabe"),
    "wasserzeichen_zeichnen": ("wasserzeichen", "zeichnen"),
    "wert_von": ("formular", "wert_von"),
    "wordart_zeichnen": ("frei_objekt_text", "wordart_zeichnen"),
    "zahl_formatieren": ("felder", "zahl_formatieren"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "deckblatt":
        from . import deckblatt as _datei
    elif datei == "felder":
        from . import felder as _datei
    elif datei == "formel_einfuegen":
        from . import formel_einfuegen as _datei
    elif datei == "formular":
        from . import formular as _datei
    elif datei == "frei_objekt_text":
        from . import frei_objekt_text as _datei
    elif datei == "wasserzeichen":
        from . import wasserzeichen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
