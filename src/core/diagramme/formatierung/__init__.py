"""Tür des Pakets ``core.diagramme.formatierung``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "FELD_STANDARD": ("diagramm_format_daten", "FELD_STANDARD"),
    "FX_NUR_HINTER": ("diagramm_format_daten", "FX_NUR_HINTER"),
    "FX_SCHLUESSEL": ("diagramm_format_daten", "FX_SCHLUESSEL"),
    "OBJEKT_DREH": ("diagramm_format_daten", "OBJEKT_DREH"),
    "PFEILE": ("diagramm_format_daten", "PFEILE"),
    "PFEIL_GROESSEN": ("diagramm_format_daten", "PFEIL_GROESSEN"),
    "PX_PT": ("diagramm_format_daten", "PX_PT"),
    "RAENDER_TITEL": ("diagramm_format_daten", "RAENDER_TITEL"),
    "STILE": ("diagramm_stile_modell", "STILE"),
    "STIL_EXTRA": ("diagramm_stile_modell", "STIL_EXTRA"),
    "STRICHTYPEN": ("diagramm_format_daten", "STRICHTYPEN"),
    "VERTIKAL": ("diagramm_format_daten", "VERTIKAL"),
    "achse_anwenden": ("diagramm_format_daten", "achse_anwenden"),
    "effekt_von": ("diagramm_format_daten", "effekt_von"),
    "feld_von": ("diagramm_format_daten", "feld_von"),
    "fuell_dict": ("diagramm_format_daten", "fuell_dict"),
    "hauptfarbe": ("diagramm_format_daten", "hauptfarbe"),
    "ist_keine": ("diagramm_format_daten", "ist_keine"),
    "linie_keine": ("diagramm_format_daten", "linie_keine"),
    "luecke_zu_breite": ("diagramm_format_daten", "luecke_zu_breite"),
    "pfeil_groessen": ("diagramm_format_daten", "pfeil_groessen"),
    "schrift_aus": ("diagramm_format_daten", "schrift_aus"),
    "stile_liste": ("diagramm_stile_modell", "stile_liste"),
    "strich_schluessel": ("diagramm_format_daten", "strich_schluessel"),
    "text_eigen": ("diagramm_format_daten", "text_eigen"),
    "textwinkel": ("diagramm_format_daten", "textwinkel"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "diagramm_format_daten":
        from . import diagramm_format_daten as _datei
    elif datei == "diagramm_stile_modell":
        from . import diagramm_stile_modell as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
