"""Tür des Pakets ``framework.ki.suche``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ANBIETER": ("websuche", "ANBIETER"),
    "ENDUNGEN": ("dokumentensuche", "ENDUNGEN"),
    "Index": ("dokumentensuche", "Index"),
    "MAX_ABSCHNITT": ("dokumentensuche", "MAX_ABSCHNITT"),
    "MAX_ANTWORT": ("suchdienst", "MAX_ANTWORT"),
    "MAX_DATEIEN": ("dokumentensuche", "MAX_DATEIEN"),
    "MAX_DATEI_BYTES": ("dokumentensuche", "MAX_DATEI_BYTES"),
    "MAX_TERME": ("dokumentensuche", "MAX_TERME"),
    "MIN_ABSCHNITT": ("dokumentensuche", "MIN_ABSCHNITT"),
    "PROTOKOLL": ("suchdienst", "PROTOKOLL"),
    "STOPP": ("dokumentensuche", "STOPP"),
    "WERKZEUGE": ("suchdienst", "WERKZEUGE"),
    "abschnitte_bilden": ("dokumentensuche", "abschnitte_bilden"),
    "aufrufen": ("suchdienst", "aufrufen"),
    "behandle": ("suchdienst", "behandle"),
    "dateien_in": ("dokumentensuche", "dateien_in"),
    "dokumentensuche_VORGABE": ("dokumentensuche", "VORGABE"),
    "dokumentensuche_als_text": ("dokumentensuche", "als_text"),
    "frage_zu_fts": ("dokumentensuche", "frage_zu_fts"),
    "fundstelle": ("dokumentensuche", "fundstelle"),
    "fundstellen_zeilen": ("dokumentensuche", "fundstellen_zeilen"),
    "lesen": ("dokument_abschnitte", "lesen"),
    "main": ("suchdienst", "main"),
    "suche": ("websuche", "suche"),
    "websuche_VORGABE": ("websuche", "VORGABE"),
    "websuche_als_text": ("websuche", "als_text"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "dokument_abschnitte":
        from . import dokument_abschnitte as _datei
    elif datei == "dokumentensuche":
        from . import dokumentensuche as _datei
    elif datei == "suchdienst":
        from . import suchdienst as _datei
    elif datei == "websuche":
        from . import websuche as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
