"""Tür des Pakets ``core.objekte.textfelder.modell``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AKTIONEN": ("formular_daten", "AKTIONEN"),
    "ALT_DECKKRAFT": ("wasserzeichen_daten", "ALT_DECKKRAFT"),
    "DATUMSFORMAT": ("formular_daten", "DATUMSFORMAT"),
    "FORMATE": ("wasserzeichen_daten", "FORMATE"),
    "FORM_STANDARD": ("frei_objekt_text_daten", "FORM_STANDARD"),
    "GROESSEN": ("wasserzeichen_daten", "GROESSEN"),
    "HORIZONTAL": ("wasserzeichen_daten", "HORIZONTAL"),
    "KASTEN_LEER": ("formular_daten", "KASTEN_LEER"),
    "KASTEN_VOLL": ("formular_daten", "KASTEN_VOLL"),
    "PLATZHALTER_FARBE": ("formular_daten", "PLATZHALTER_FARBE"),
    "RICHTUNGEN": ("frei_objekt_text_daten", "RICHTUNGEN"),
    "STANDARD_FARBE": ("wasserzeichen_daten", "STANDARD_FARBE"),
    "STANDARD_MASS": ("frei_objekt_text_daten", "STANDARD_MASS"),
    "TEXTFELD_FUELL": ("frei_objekt_text_daten", "TEXTFELD_FUELL"),
    "TEXTFELD_RAND": ("frei_objekt_text_daten", "TEXTFELD_RAND"),
    "TEXTFELD_STANDARD": ("frei_objekt_text_daten", "TEXTFELD_STANDARD"),
    "TEXTRAND": ("frei_objekt_text_daten", "TEXTRAND"),
    "TEXT_ARTEN": ("frei_objekt_text_daten", "TEXT_ARTEN"),
    "VERTIKAL": ("wasserzeichen_daten", "VERTIKAL"),
    "VORGABEN": ("wasserzeichen_daten", "VORGABEN"),
    "WORDART_STANDARD": ("frei_objekt_text_daten", "WORDART_STANDARD"),
    "ZOOMS": ("wasserzeichen_daten", "ZOOMS"),
    "alle_zuruecksetzen": ("formular_daten", "alle_zuruecksetzen"),
    "bereiche": ("formular_daten", "bereiche"),
    "da": ("wasserzeichen_daten", "da"),
    "daten": ("formular_daten", "daten"),
    "einfuegen": ("formular_daten", "einfuegen"),
    "ersetzen": ("formular_daten", "ersetzen"),
    "feld_an": ("formular_daten", "feld_an"),
    "formular_daten_ARTEN": ("formular_daten", "ARTEN"),
    "frei_objekt_text_daten_ARTEN": ("frei_objekt_text_daten", "ARTEN"),
    "ist_leer": ("formular_daten", "ist_leer"),
    "kasten_umschalten": ("formular_daten", "kasten_umschalten"),
    "laeufe_ab": ("frei_objekt_text_daten", "laeufe_ab"),
    "laeufe_zusammen": ("frei_objekt_text_daten", "laeufe_zusammen"),
    "meta": ("formular_daten", "meta"),
    "meta_lesen": ("formular_daten", "meta_lesen"),
    "meta_text": ("formular_daten", "meta_text"),
    "nur_formulardaten": ("formular_daten", "nur_formulardaten"),
    "wert_von": ("formular_daten", "wert_von"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "formular_daten":
        from . import formular_daten as _datei
    elif datei == "frei_objekt_text_daten":
        from . import frei_objekt_text_daten as _datei
    elif datei == "wasserzeichen_daten":
        from . import wasserzeichen_daten as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
