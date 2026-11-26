"""Tür des Pakets ``writer.funktionen.ansicht``: öffentliche Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ANSICHTSARTEN": ("statusleiste", "ANSICHTSARTEN"),
    "Ansichtsart": ("statusleiste", "Ansichtsart"),
    "Layoutsicht": ("layout", "Layoutsicht"),
    "ZOOMWAHLEN": ("statusleiste", "ZOOMWAHLEN"),
    "ZOOM_PROZENT_MAX": ("statusleiste", "ZOOM_PROZENT_MAX"),
    "ZOOM_PROZENT_MIN": ("statusleiste", "ZOOM_PROZENT_MIN"),
    "Zoomwahl": ("statusleiste", "Zoomwahl"),
    "ausgabe_als_pdf": ("ausgabe", "ausgabe_als_pdf"),
    "ausgabe_anzahl": ("ausgabe", "ausgabe_anzahl"),
    "ausgabe_aus_datei": ("ausgabe", "ausgabe_aus_datei"),
    "ausgabe_aus_geruest": ("ausgabe", "ausgabe_aus_geruest"),
    "ausgabe_blasen": ("ausgabe", "ausgabe_blasen"),
    "ausgabe_oeffnen": ("ausgabe", "ausgabe_oeffnen"),
    "ausgabe_schliessen": ("ausgabe", "ausgabe_schliessen"),
    "ausgabe_seite_mm": ("ausgabe", "ausgabe_seite_mm"),
    "ausgabe_seitenbild": ("ausgabe", "ausgabe_seitenbild"),
    "bewegen": ("layout", "bewegen"),
    "cursor_rechteck": ("layout", "cursor_rechteck"),
    "cursorbild": ("seitenbilder", "cursorbild"),
    "layout_berechnen": ("layout", "berechnen"),
    "layout_option_setzen": ("layout", "option_setzen"),
    "layout_silben_setzen": ("layout", "silben_setzen"),
    "layout_verwerfen": ("layout", "verwerfen"),
    "seitenbild": ("seitenbilder", "seitenbild"),
    "ueberlagerung_setzen": ("seitenbilder", "ueberlagerung_setzen"),
    "ueberlagerung_stand": ("seitenbilder", "ueberlagerung_stand"),
    "ueberlagerungsbild": ("seitenbilder", "ueberlagerungsbild"),
    "vorschau_brief": ("vorschau", "vorschau_brief"),
    "vorschau_kopie": ("vorschau", "vorschau_kopie"),
    "vorschau_schliessen": ("vorschau", "vorschau_schliessen"),
    "wort_bei": ("layout", "wort_bei"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "ausgabe":
        from . import ausgabe as _datei
    elif datei == "layout":
        from . import layout as _datei
    elif datei == "vorschau":
        from . import vorschau as _datei
    elif datei == "seitenbilder":
        from . import seitenbilder as _datei
    elif datei == "statusleiste":
        from . import statusleiste as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
