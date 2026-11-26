"""Tür des Pakets ``writer.funktionen.objekte``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "alle_zuruecksetzen": ("formular", "alle_zuruecksetzen"),
    "als_text": ("wordart", "als_text"),
    "aufzaehlung": ("smartart", "aufzaehlung"),
    "aus_text": ("wordart", "aus_text"),
    "bildeffekte_abschluesse": ("bildeffekte", "bildeffekte_abschluesse"),
    "da": ("wasserzeichen", "da"),
    "deckblatt_entfernen": ("deckblatt", "deckblatt_entfernen"),
    "deckblatt_felder": ("deckblatt", "deckblatt_felder"),
    "deckblatt_gruppe": ("deckblatt", "deckblatt_gruppe"),
    "deckblatt_namen": ("deckblatt", "deckblatt_namen"),
    "diagramm_pfeil_groessen": ("diagrammformat", "diagramm_pfeil_groessen"),
    "diagramm_pfeile": ("diagrammformat", "diagramm_pfeile"),
    "diagramm_strichtypen": ("diagrammformat", "diagramm_strichtypen"),
    "diagramm_vertikal_ausrichtungen": ("diagrammformat", "diagramm_vertikal_ausrichtungen"),
    "einfuegen_daten": ("smartart", "einfuegen_daten"),
    "ersetzen": ("formular", "ersetzen"),
    "feld_an": ("formular", "feld_an"),
    "form_einfuegen": ("smartart", "form_einfuegen"),
    "format_lesen": ("smartart", "format_lesen"),
    "format_mischen": ("smartart", "format_mischen"),
    "format_schluessel": ("smartart", "format_schluessel"),
    "formular_aktion_drucken": ("formular", "formular_aktion_drucken"),
    "formular_aktion_pdf": ("formular", "formular_aktion_pdf"),
    "formular_aktion_zuruecksetzen": ("formular", "formular_aktion_zuruecksetzen"),
    "formular_aktionen": ("formular", "formular_aktionen"),
    "formular_datumsformat": ("formular", "formular_datumsformat"),
    "formular_einfuegen": ("formular", "einfuegen"),
    "hat_effekt": ("wordart", "hat_effekt"),
    "inline_an": ("objektangaben", "inline_an"),
    "inline_der_auswahl": ("objektangaben", "inline_der_auswahl"),
    "inline_gewaehlt": ("objektangaben", "inline_gewaehlt"),
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
    "muster_vorlagen": ("muster", "muster_vorlagen"),
    "name_von": ("muster", "name_von"),
    "nur_formulardaten": ("formular", "nur_formulardaten"),
    "objekt_angabe": ("objektangaben", "objekt_angabe"),
    "objekt_angabe_speichern": ("objektangaben", "objekt_angabe_speichern"),
    "objekt_textfelder": ("objektangaben", "objekt_textfelder"),
    "ohne_hilfsangaben": ("freie_objekte", "ohne_hilfsangaben"),
    "reflektion_vorgaben": ("wordart", "reflektion_vorgaben"),
    "schatten_vorgaben": ("wordart", "schatten_vorgaben"),
    "schnelltabelle_einfuegen": ("schnelltabelle", "einfuegen"),
    "schnelltabellen_namen": ("schnelltabelle", "schnelltabellen_namen"),
    "strich_schluessel": ("diagrammformat", "strich_schluessel"),
    "tabelle_gewaehlt_zustaende": ("tabellenzustand", "tabelle_gewaehlt_zustaende"),
    "tabellen_zustand": ("tabellenzustand", "tabellen_zustand"),
    "tabellenmodus": ("tabellenzustand", "tabellenmodus"),
    "text_aus_knoten": ("smartart", "text_aus_knoten"),
    "text_gegen_knoten": ("smartart", "text_gegen_knoten"),
    "textfeld_hat_nachfolger": ("freie_objekte", "textfeld_hat_nachfolger"),
    "textfeld_standard": ("freie_objekte", "textfeld_standard"),
    "verschieben": ("smartart", "verschieben"),
    "vorgabe": ("bildeffekte", "vorgabe"),
    "wasserzeichen_formate": ("wasserzeichen", "wasserzeichen_formate"),
    "wasserzeichen_groessen": ("wasserzeichen", "wasserzeichen_groessen"),
    "wasserzeichen_horizontal": ("wasserzeichen", "wasserzeichen_horizontal"),
    "wasserzeichen_standard_farbe": ("wasserzeichen", "wasserzeichen_standard_farbe"),
    "wasserzeichen_vertikal": ("wasserzeichen", "wasserzeichen_vertikal"),
    "wasserzeichen_vorgaben": ("wasserzeichen", "wasserzeichen_vorgaben"),
    "wasserzeichen_zooms": ("wasserzeichen", "wasserzeichen_zooms"),
    "wert_von": ("formular", "wert_von"),
    "wordart_beleuchtungen": ("wordart", "wordart_beleuchtungen"),
    "wordart_materialien": ("wordart", "wordart_materialien"),
    "wordart_px": ("wordart", "wordart_px"),
    "wordart_standard": ("freie_objekte", "wordart_standard"),
    "wordart_vorgaben": ("wordart", "wordart_vorgaben"),
    "wordart_warp_formen": ("wordart", "wordart_warp_formen"),
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
    elif datei == "objektangaben":
        from . import objektangaben as _datei
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
