"""Tür des Pakets ``core.layout.drucklayout.ausgabe.seite``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ALT_DECKKRAFT": ("wasserzeichen", "ALT_DECKKRAFT"),
    "AUSWASCHEN": ("wasserzeichen", "AUSWASCHEN"),
    "DURCHSICHTIG": ("seitenueberlagerung", "DURCHSICHTIG"),
    "HINTER_DEM_TEXT": ("seitenrenderer", "HINTER_DEM_TEXT"),
    "KOPF_MM": ("seitenrahmen", "KOPF_MM"),
    "NOTENLINIE": ("seitenrenderer", "NOTENLINIE"),
    "PX_JE_PT": ("kopffuss", "PX_JE_PT"),
    "SCHWARZ": ("seitenrahmen", "SCHWARZ"),
    "STANDARD_FARBE": ("wasserzeichen", "STANDARD_FARBE"),
    "STANDARD_PX": ("kopffuss", "STANDARD_PX"),
    "SeitenRenderer": ("seitenrenderer", "SeitenRenderer"),
    "TREFFER_FARBE": ("seitenueberlagerung", "TREFFER_FARBE"),
    "Ueberlagerung": ("seitenueberlagerung", "Ueberlagerung"),
    "abstaende_pt": ("seitenrahmen", "abstaende_pt"),
    "bild_bytes": ("wasserzeichen", "bild_bytes"),
    "da": ("wasserzeichen", "da"),
    "deckkraft": ("wasserzeichen", "deckkraft"),
    "kopffuss_schrift": ("kopffuss", "schrift"),
    "kunst_zeichnen": ("seitenrahmen", "kunst_zeichnen"),
    "lage": ("wasserzeichen", "lage"),
    "rechteck": ("seitenrahmen", "rechteck"),
    "rendere_cursor": ("seitenueberlagerung", "rendere_cursor"),
    "rendere_ueberlagerung": ("seitenueberlagerung", "rendere_ueberlagerung"),
    "seitenrahmen_PX_JE_MM": ("seitenrahmen", "PX_JE_MM"),
    "seitenschmuck_PX_JE_MM": ("seitenschmuck", "PX_JE_MM"),
    "wasserzeichen_PX_JE_MM": ("wasserzeichen", "PX_JE_MM"),
    "wasserzeichen_schrift": ("wasserzeichen", "schrift"),
    "zeichne": ("wasserzeichen", "zeichne"),
    "zeichne_seitenschmuck": ("seitenschmuck", "zeichne_seitenschmuck"),
    "zeichne_zeile": ("kopffuss", "zeichne_zeile"),
    "zeichnen": ("seitenrahmen", "zeichnen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "kopffuss":
        from . import kopffuss as _datei
    elif datei == "seitenrahmen":
        from . import seitenrahmen as _datei
    elif datei == "seitenrenderer":
        from . import seitenrenderer as _datei
    elif datei == "seitenschmuck":
        from . import seitenschmuck as _datei
    elif datei == "seitenueberlagerung":
        from . import seitenueberlagerung as _datei
    elif datei == "wasserzeichen":
        from . import wasserzeichen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
