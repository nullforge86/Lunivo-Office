"""Tür des Pakets ``writer.funktionen.objekte``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ABSCHLUSS": ("bildeffekte", "ABSCHLUSS"),
    "AKTIONEN": ("formular", "AKTIONEN"),
    "AKTION_DRUCKEN": ("formular", "AKTION_DRUCKEN"),
    "AKTION_PDF": ("formular", "AKTION_PDF"),
    "AKTION_ZURUECKSETZEN": ("formular", "AKTION_ZURUECKSETZEN"),
    "BELEUCHTUNG": ("wordart", "BELEUCHTUNG"),
    "DATUMSFORMAT": ("formular", "DATUMSFORMAT"),
    "FORMATE": ("wasserzeichen", "FORMATE"),
    "GROESSEN": ("wasserzeichen", "GROESSEN"),
    "HORIZONTAL": ("wasserzeichen", "HORIZONTAL"),
    "MATERIAL": ("wordart", "MATERIAL"),
    "MUSTER": ("muster", "MUSTER"),
    "NAMEN": ("deckblatt", "NAMEN"),
    "PFEILE": ("diagrammformat", "PFEILE"),
    "PFEIL_GROESSEN": ("diagrammformat", "PFEIL_GROESSEN"),
    "PX": ("wordart", "PX"),
    "SCHNELLTABELLEN": ("schnelltabelle", "SCHNELLTABELLEN"),
    "STANDARD_FARBE": ("wasserzeichen", "STANDARD_FARBE"),
    "STRICHTYPEN": ("diagrammformat", "STRICHTYPEN"),
    "TABELLE_GEWAEHLT": ("tabellenzustand", "TABELLE_GEWAEHLT"),
    "TEXTFELD_STANDARD": ("freie_objekte", "TEXTFELD_STANDARD"),
    "VORGABEN": ("wasserzeichen", "VORGABEN"),
    "WARP_FORMEN": ("wordart", "WARP_FORMEN"),
    "WORDART_STANDARD": ("freie_objekte", "WORDART_STANDARD"),
    "ZOOMS": ("wasserzeichen", "ZOOMS"),
    "alle_zuruecksetzen": ("formular", "alle_zuruecksetzen"),
    "als_text": ("wordart", "als_text"),
    "aufzaehlung": ("smartart", "aufzaehlung"),
    "aus_text": ("wordart", "aus_text"),
    "da": ("wasserzeichen", "da"),
    "deckblatt_entfernen": ("deckblatt", "deckblatt_entfernen"),
    "diagrammformat_VERTIKAL": ("diagrammformat", "VERTIKAL"),
    "einfuegen_daten": ("smartart", "einfuegen_daten"),
    "ersetzen": ("formular", "ersetzen"),
    "feld_an": ("formular", "feld_an"),
    "form_einfuegen": ("smartart", "form_einfuegen"),
    "format_lesen": ("smartart", "format_lesen"),
    "format_mischen": ("smartart", "format_mischen"),
    "format_schluessel": ("smartart", "format_schluessel"),
    "formular_einfuegen": ("formular", "einfuegen"),
    "hat_effekt": ("wordart", "hat_effekt"),
    "ist_leer": ("formular", "ist_leer"),
    "ist_metafile_emf": ("vektorbilder", "ist_metafile_emf"),
    "ist_metafile_wmf": ("vektorbilder", "ist_metafile_wmf"),
    "ist_verknuepft": ("freie_objekte", "ist_verknuepft"),
    "kann": ("smartart", "kann"),
    "kasten_umschalten": ("formular", "kasten_umschalten"),
    "katalog": ("smartart", "katalog"),
    "knoten_gewaehlt": ("smartart", "knoten_gewaehlt"),
    "knoten_index": ("smartart", "knoten_index"),
    "knoten_text": ("smartart", "knoten_text"),
    "knoten_von": ("smartart", "knoten_von"),
    "knoten_waehlbar": ("smartart", "knoten_waehlbar"),
    "knotentext": ("smartart", "knotentext"),
    "leuchten_vorgaben": ("wordart", "leuchten_vorgaben"),
    "level": ("smartart", "level"),
    "meta": ("formular", "meta"),
    "metafile_masse_px": ("vektorbilder", "metafile_masse_px"),
    "metafile_rgba": ("vektorbilder", "metafile_rgba"),
    "name_von": ("muster", "name_von"),
    "nur_formulardaten": ("formular", "nur_formulardaten"),
    "ohne_hilfsangaben": ("freie_objekte", "ohne_hilfsangaben"),
    "reflektion_vorgaben": ("wordart", "reflektion_vorgaben"),
    "schatten_vorgaben": ("wordart", "schatten_vorgaben"),
    "schnelltabelle_einfuegen": ("schnelltabelle", "einfuegen"),
    "strich_schluessel": ("diagrammformat", "strich_schluessel"),
    "tabellen_zustand": ("tabellenzustand", "tabellen_zustand"),
    "tabellenmodus": ("tabellenzustand", "tabellenmodus"),
    "text_aus_knoten": ("smartart", "text_aus_knoten"),
    "text_gegen_knoten": ("smartart", "text_gegen_knoten"),
    "textfeld_hat_nachfolger": ("freie_objekte", "textfeld_hat_nachfolger"),
    "verschieben": ("smartart", "verschieben"),
    "vorgabe": ("bildeffekte", "vorgabe"),
    "wasserzeichen_VERTIKAL": ("wasserzeichen", "VERTIKAL"),
    "wert_von": ("formular", "wert_von"),
    "wordart_vorgaben": ("wordart", "wordart_vorgaben"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "bildeffekte":
        from . import bildeffekte as _datei
    elif datei == "deckblatt":
        from . import deckblatt as _datei
    elif datei == "diagrammformat":
        from . import diagrammformat as _datei
    elif datei == "formular":
        from . import formular as _datei
    elif datei == "freie_objekte":
        from . import freie_objekte as _datei
    elif datei == "muster":
        from . import muster as _datei
    elif datei == "schnelltabelle":
        from . import schnelltabelle as _datei
    elif datei == "smartart":
        from . import smartart as _datei
    elif datei == "tabellenzustand":
        from . import tabellenzustand as _datei
    elif datei == "vektorbilder":
        from . import vektorbilder as _datei
    elif datei == "wasserzeichen":
        from . import wasserzeichen as _datei
    elif datei == "wordart":
        from . import wordart as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
