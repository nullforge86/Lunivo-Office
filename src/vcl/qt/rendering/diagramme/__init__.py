"""Tür des Pakets ``vcl.qt.rendering.diagramme``: alle öffentlichen Namen des Pakets. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen (keine zusätzlichen Importzyklen). Gibt es einen Namen in
mehreren Dateien, heißt er hier ``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "EFFEKTE": ("diagramm_teile", "EFFEKTE"),
    "FARBSCHEMEN": ("diagramm_stile", "FARBSCHEMEN"),
    "FORMAT_SCHLUESSEL": ("diagramm_teile", "FORMAT_SCHLUESSEL"),
    "NAMEN_QUELLEN": ("diagramm", "NAMEN_QUELLEN"),
    "bild": ("diagramm", "bild"),
    "bild_aus_daten": ("diagramm", "bild_aus_daten"),
    "bild_dekodieren": ("diagramm_format", "bild_dekodieren"),
    "bild_kodieren": ("diagramm_format", "bild_kodieren"),
    "box_rect": ("diagramm_format", "box_rect"),
    "diagramm_teil_format_lesen": ("diagramm_teile", "diagramm_teil_format_lesen"),
    "diagramm_teil_format_setzen": ("diagramm_teile", "diagramm_teil_format_setzen"),
    "farbschemen_flach": ("diagramm_stile", "farbschemen_flach"),
    "farbschemen_gruppen": ("diagramm_stile", "farbschemen_gruppen"),
    "flaeche_bild": ("diagramm_format", "flaeche_bild"),
    "flaeche_zeichnen": ("diagramm_format", "flaeche_zeichnen"),
    "fx_normal": ("diagramm_format", "fx_normal"),
    "namen_angewendet": ("diagramm", "namen_angewendet"),
    "pfeil_zeichnen": ("diagramm_format", "pfeil_zeichnen"),
    "pinsel": ("diagramm_format", "pinsel"),
    "rahmen_zeichnen": ("diagramm_format", "rahmen_zeichnen"),
    "stift": ("diagramm_format", "stift"),
    "teil_bei": ("diagramm_teile", "teil_bei"),
    "teil_geo": ("diagramm", "teil_geo"),
    "teil_gewaehlt": ("diagramm_teile", "teil_gewaehlt"),
    "teil_name": ("diagramm_teile", "teil_name"),
    "teil_rechtecke": ("diagramm", "teil_rechtecke"),
    "teil_waehlen": ("diagramm_teile", "teil_waehlen"),
    "teil_zeichnen": ("diagramm_format", "teil_zeichnen"),
    "teile": ("diagramm", "teile"),
    "text_feld": ("diagramm_format", "text_feld"),
    "textfarbe": ("diagramm_format", "textfarbe"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "diagramm":
        from . import diagramm as _datei
    elif datei == "diagramm_format":
        from . import diagramm_format as _datei
    elif datei == "diagramm_stile":
        from . import diagramm_stile as _datei
    elif datei == "diagramm_teile":
        from . import diagramm_teile as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
