"""Tür des Pakets ``vcl.qt.rendering.formen``: alle öffentlichen Namen des Pakets. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen (keine zusätzlichen Importzyklen). Gibt es einen Namen in
mehreren Dateien, heißt er hier ``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ANPASS": ("formen_anpassen", "ANPASS"),
    "AUSRICHTEN": ("bildlayout", "AUSRICHTEN"),
    "AUSR_H": ("bildlayout", "AUSR_H"),
    "AUSR_V": ("bildlayout", "AUSR_V"),
    "BD_svg_daten": ("bilddaten", "BD_svg_daten"),
    "BILD_ARTEN": ("bildwerkzeuge", "BILD_ARTEN"),
    "BildQuelle": ("bilddaten", "BildQuelle"),
    "C": ("freiform", "C"),
    "D": ("freiform", "D"),
    "DATUMSFORMATE": ("einfuegen", "DATUMSFORMATE"),
    "DATUM_SPRACHEN": ("einfuegen", "DATUM_SPRACHEN"),
    "DECKBLATT_VORLAGEN": ("einfuegen", "DECKBLATT_VORLAGEN"),
    "DIAGRAMMARTEN": ("einfuegen", "DIAGRAMMARTEN"),
    "ERSATZ_SEITE": ("bilddaten", "ERSATZ_SEITE"),
    "FORMEN": ("einfuegen", "FORMEN"),
    "FX_SCHLUESSEL": ("bildlayout", "FX_SCHLUESSEL"),
    "GLEICHUNGEN": ("einfuegen", "GLEICHUNGEN"),
    "GRENZE": ("bildzuschnitt", "GRENZE"),
    "KATEGORIEN": ("formen_katalog", "KATEGORIEN"),
    "KOMPRIMIEREN_FAKTOR": ("bildwerkzeuge", "KOMPRIMIEREN_FAKTOR"),
    "KUNST": ("seitenrahmen", "KUNST"),
    "L": ("freiform", "L"),
    "LINIENARTEN": ("linie", "LINIENARTEN"),
    "Linie": ("linie", "Linie"),
    "M": ("freiform", "M"),
    "MAX_ABLAGE_BYTES": ("bilddaten", "MAX_ABLAGE_BYTES"),
    "MAX_DATEI_BYTES": ("bilddaten", "MAX_DATEI_BYTES"),
    "NAME": ("freiform", "NAME"),
    "NS_SVG": ("bilddaten", "NS_SVG"),
    "ORIGINAL_DOCX": ("bilddaten", "ORIGINAL_DOCX"),
    "ORIGINAL_DOCX_METAFILE": ("bilddaten", "ORIGINAL_DOCX_METAFILE"),
    "ORIGINAL_ODT": ("bilddaten", "ORIGINAL_ODT"),
    "Pfad": ("formen_katalog", "Pfad"),
    "QtRenderBackend": ("rendering", "QtRenderBackend"),
    "SCHRITT": ("bildwerkzeuge", "SCHRITT"),
    "STANDARD": ("bildlayout", "STANDARD"),
    "STILE": ("linie", "STILE"),
    "TEXTFELD_VERTIKAL": ("form_einfuegen", "TEXTFELD_VERTIKAL"),
    "UMBRUCH_FENSTER": ("bildlayout", "UMBRUCH_FENSTER"),
    "UMBRUCH_MODELL": ("bildlayout", "UMBRUCH_MODELL"),
    "UMGEKEHRT_H": ("bildlayout", "UMGEKEHRT_H"),
    "UMGEKEHRT_V": ("bildlayout", "UMGEKEHRT_V"),
    "VERHAELTNISSE": ("bildzuschnitt", "VERHAELTNISSE"),
    "WORDART_STANDARDTEXT": ("einfuegen", "WORDART_STANDARDTEXT"),
    "WORDART_STILE": ("einfuegen", "WORDART_STILE"),
    "WORDART_VORGABEN": ("einfuegen", "WORDART_VORGABEN"),
    "Z": ("freiform", "Z"),
    "ZB_RAND": ("formen", "ZB_RAND"),
    "ZB_VERSATZ": ("formen", "ZB_VERSATZ"),
    "ZEICHNER": ("frei_objekt", "ZEICHNER"),
    "abschluss_oben": ("bildeffekte", "abschluss_oben"),
    "abschluss_symbol": ("bildeffekte", "abschluss_symbol"),
    "anpass_griff": ("formen", "anpass_griff"),
    "anpass_griffe": ("formen", "anpass_griffe"),
    "anpass_setzen": ("formen", "anpass_setzen"),
    "anpassen": ("formen", "anpassen"),
    "anwenden": ("bildlayout", "anwenden"),
    "anzeigegroesse": ("bilddaten", "anzeigegroesse"),
    "art_aus_docx": ("linie", "art_aus_docx"),
    "art_gewaehlt": ("frei_objekt", "art_gewaehlt"),
    "aus_datei": ("bildwerkzeuge", "aus_datei"),
    "aus_form": ("freiform", "aus_form"),
    "aus_pfad": ("freiform", "aus_pfad"),
    "aus_ziehen": ("bildzuschnitt", "aus_ziehen"),
    "ausrichten": ("bildlayout", "ausrichten"),
    "bild_aus_datei": ("bilddaten", "bild_aus_datei"),
    "bild_aus_daten": ("freie_bilder", "bild_aus_daten"),
    "bild_aus_svg": ("bilddaten", "bild_aus_svg"),
    "bild_einfuegen_drehen": ("bild_einfuegen", "drehen"),
    "bild_ersetzen": ("bild_einfuegen", "bild_ersetzen"),
    "bild_nachbearbeiten": ("bildeffekte", "bild_nachbearbeiten"),
    "bild_original": ("bild_einfuegen", "bild_original"),
    "bild_zeichnen": ("freie_bilder", "bild_zeichnen"),
    "bilddaten_zeichnen": ("bilddaten", "zeichnen"),
    "bildlayout_drehen": ("bildlayout", "drehen"),
    "bildlayout_lesen": ("bildlayout", "lesen"),
    "bildlayout_ziel": ("bildlayout", "ziel"),
    "bildwerkzeuge_aendern": ("bildwerkzeuge", "aendern"),
    "bildwerkzeuge_zuruecksetzen": ("bildwerkzeuge", "zuruecksetzen"),
    "bildzuschnitt_anzeige": ("bildzuschnitt", "anzeige"),
    "bildzuschnitt_hat": ("bildzuschnitt", "hat"),
    "bildzuschnitt_lesen": ("bildzuschnitt", "lesen"),
    "bildzuschnitt_setzen": ("bildzuschnitt", "setzen"),
    "bildzuschnitt_zuruecksetzen": ("bildzuschnitt", "zuruecksetzen"),
    "datei_symbol_bild": ("bild_einfuegen", "datei_symbol_bild"),
    "daten_lesen": ("frei_objekt", "daten_lesen"),
    "daten_still": ("frei_objekt", "daten_still"),
    "datum_feldanweisung": ("einfuegen", "datum_feldanweisung"),
    "datum_text": ("einfuegen", "datum_text"),
    "deckblatt_einfuegen": ("einfuegen", "deckblatt_einfuegen"),
    "diagramm_bild": ("einfuegen", "diagramm_bild"),
    "docx_wert": ("linie", "docx_wert"),
    "drehung_3d": ("bildeffekte", "drehung_3d"),
    "duoton": ("freie_bilder", "duoton"),
    "ebene": ("bildlayout", "ebene"),
    "entpacken": ("bilddaten", "entpacken"),
    "extrusion_zeichnen": ("bildeffekte", "extrusion_zeichnen"),
    "farbe_anwenden": ("bild_einfuegen", "farbe_anwenden"),
    "farbe_aus_element": ("freie_bilder", "farbe_aus_element"),
    "farbe_transparent": ("bildwerkzeuge", "farbe_transparent"),
    "form": ("bildzuschnitt", "form"),
    "form_bild": ("form_einfuegen", "form_bild"),
    "form_wechseln": ("formen", "form_wechseln"),
    "format_aus_panel": ("bildlayout", "format_aus_panel"),
    "format_lesen": ("bildlayout", "format_lesen"),
    "format_merken": ("bildlayout", "format_merken"),
    "format_setzen": ("bildlayout", "format_setzen"),
    "format_uebertragen": ("bildlayout", "format_uebertragen"),
    "formen_aendern": ("formen", "aendern"),
    "formen_anpassen_anpassbar": ("formen_anpassen", "anpassbar"),
    "formen_anpassen_pfad": ("formen_anpassen", "pfad"),
    "formen_anpassen_setzen": ("formen_anpassen", "setzen"),
    "formen_katalog_anpassbar": ("formen_katalog", "anpassbar"),
    "formen_katalog_hat": ("formen_katalog", "hat"),
    "formen_katalog_pfad": ("formen_katalog", "pfad"),
    "formen_kategorien": ("bildzuschnitt", "formen_kategorien"),
    "formstil": ("formen_stile", "formstil"),
    "formstile_raster": ("formen_stile", "formstile_raster"),
    "frei_aendern": ("bildlayout", "frei_aendern"),
    "frei_bild": ("bildwerkzeuge", "frei_bild"),
    "frei_bild_ersetzen": ("bildlayout", "frei_bild_ersetzen"),
    "frei_daten": ("formen", "frei_daten"),
    "frei_entfernen": ("bildlayout", "frei_entfernen"),
    "frei_objekt_aendern": ("frei_objekt", "aendern"),
    "frei_objekt_bild_einfuegen": ("frei_objekt", "bild_einfuegen"),
    "frei_objekt_einfuegen": ("frei_objekt", "einfuegen"),
    "frei_objekt_zeichnen": ("frei_objekt", "zeichnen"),
    "frei_objekt_ziel": ("frei_objekt", "ziel"),
    "frei_original": ("bildlayout", "frei_original"),
    "frei_original_groesse": ("bildlayout", "frei_original_groesse"),
    "freie_bilder_rechteck": ("freie_bilder", "rechteck"),
    "freiform_einfuegen": ("freiform", "einfuegen"),
    "freiform_pfad": ("freiform", "pfad"),
    "fuell_pinsel": ("freie_bilder", "fuell_pinsel"),
    "fuellbild_setzen": ("bildlayout", "fuellbild_setzen"),
    "fuer_schreiben": ("bilddaten", "fuer_schreiben"),
    "fx_alle": ("bildlayout", "fx_alle"),
    "geschlossen": ("freiform", "geschlossen"),
    "gespiegelt": ("bildeffekte", "gespiegelt"),
    "griffe": ("formen_anpassen", "griffe"),
    "gruppe_aufheben": ("formen", "gruppe_aufheben"),
    "gruppieren": ("formen", "gruppieren"),
    "in_zeichenbereich": ("formen", "in_zeichenbereich"),
    "initiale": ("einfuegen", "initiale"),
    "innen": ("freiform", "innen"),
    "ist_linie": ("formen_katalog", "ist_linie"),
    "ist_svg": ("bilddaten", "ist_svg"),
    "kachel": ("muster", "kachel"),
    "kern_bild": ("anzeige", "kern_bild"),
    "kern_malen": ("anzeige", "kern_malen"),
    "kette_aktualisieren": ("frei_objekt", "kette_aktualisieren"),
    "knoten": ("freiform", "knoten"),
    "komprimieren": ("bildwerkzeuge", "komprimieren"),
    "korrektur_schritt": ("bildwerkzeuge", "korrektur_schritt"),
    "korrektur_setzen": ("bildwerkzeuge", "korrektur_setzen"),
    "korrigiert": ("bildwerkzeuge", "korrigiert"),
    "loeschen": ("freiform", "loeschen"),
    "loesen": ("frei_objekt", "loesen"),
    "margins_from_qt": ("geometrie", "margins_from_qt"),
    "margins_to_qt": ("geometrie", "margins_to_qt"),
    "masse_lesen": ("bildlayout", "masse_lesen"),
    "masse_setzen": ("bildlayout", "masse_setzen"),
    "menue_rect": ("sprechblasen", "menue_rect"),
    "merken": ("bilddaten", "merken"),
    "mit_ausrichtung_lesen": ("bilddaten", "mit_ausrichtung_lesen"),
    "naechste_kante": ("freiform", "naechste_kante"),
    "namen": ("formen_katalog", "namen"),
    "pfad_zu_vektor": ("pfad", "pfad_zu_vektor"),
    "piktogramm_bild": ("bild_einfuegen", "piktogramm_bild"),
    "pinsel": ("muster", "pinsel"),
    "platzhalter": ("bilddaten", "platzhalter"),
    "png_bytes": ("bilddaten", "png_bytes"),
    "point_from_qt": ("geometrie", "point_from_qt"),
    "point_to_qt": ("geometrie", "point_to_qt"),
    "qimage_einfuegen": ("bild_einfuegen", "qimage_einfuegen"),
    "quelle_zu": ("bilddaten", "quelle_zu"),
    "rect_from_qt": ("geometrie", "rect_from_qt"),
    "rect_to_qt": ("geometrie", "rect_to_qt"),
    "rollen": ("freiform", "rollen"),
    "seite_malen": ("anzeige", "seite_malen"),
    "seitenrahmen_rechteck": ("seitenrahmen", "rechteck"),
    "seitenrahmen_zeichnen": ("seitenrahmen", "zeichnen"),
    "size_from_qt": ("geometrie", "size_from_qt"),
    "size_to_qt": ("geometrie", "size_to_qt"),
    "skala": ("bildzuschnitt", "skala"),
    "skala_text": ("bildzuschnitt", "skala_text"),
    "sperre": ("bildwerkzeuge", "sperre"),
    "sperre_umschalten": ("bildwerkzeuge", "sperre_umschalten"),
    "sprechblasen_zeichnen": ("sprechblasen", "zeichnen"),
    "standard": ("formen_anpassen", "standard"),
    "svg_bereinigen": ("bilddaten", "svg_bereinigen"),
    "svg_raster": ("bilddaten", "svg_raster"),
    "text_aus_datei": ("einfuegen", "text_aus_datei"),
    "text_bereich": ("frei_objekt", "text_bereich"),
    "text_werte_anwenden": ("frei_objekt", "text_werte_anwenden"),
    "text_werte_lesen": ("frei_objekt", "text_werte_lesen"),
    "textfeld": ("einfuegen", "textfeld"),
    "textur_textur": ("textur", "textur"),
    "transparent": ("bildwerkzeuge", "transparent"),
    "uebernehmen": ("bilddaten", "uebernehmen"),
    "unter_zeichnen": ("bildeffekte", "unter_zeichnen"),
    "vektor_zu_pfad": ("pfad", "vektor_zu_pfad"),
    "verbindung": ("sprechblasen", "verbindung"),
    "verknuepfen": ("frei_objekt", "verknuepfen"),
    "versatz_fuer": ("freie_bilder", "versatz_fuer"),
    "verschieben": ("freiform", "verschieben"),
    "verschieben_wahl": ("bildlayout", "verschieben_wahl"),
    "vorlage": ("formen", "vorlage"),
    "weiche_kanten": ("bildeffekte", "weiche_kanten"),
    "wert_aus_punkt": ("formen_anpassen", "wert_aus_punkt"),
    "werte": ("bildwerkzeuge", "werte"),
    "zeichenbereich_bild": ("formen", "zeichenbereich_bild"),
    "zeichenbereich_einfuegen": ("formen", "zeichenbereich_einfuegen"),
    "zuschneiden": ("bild_einfuegen", "zuschneiden"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "anzeige":
        from . import anzeige as _datei
    elif datei == "bild_einfuegen":
        from . import bild_einfuegen as _datei
    elif datei == "bilddaten":
        from . import bilddaten as _datei
    elif datei == "bildeffekte":
        from . import bildeffekte as _datei
    elif datei == "bildlayout":
        from . import bildlayout as _datei
    elif datei == "bildwerkzeuge":
        from . import bildwerkzeuge as _datei
    elif datei == "bildzuschnitt":
        from . import bildzuschnitt as _datei
    elif datei == "einfuegen":
        from . import einfuegen as _datei
    elif datei == "form_einfuegen":
        from . import form_einfuegen as _datei
    elif datei == "formen":
        from . import formen as _datei
    elif datei == "formen_anpassen":
        from . import formen_anpassen as _datei
    elif datei == "formen_katalog":
        from . import formen_katalog as _datei
    elif datei == "formen_stile":
        from . import formen_stile as _datei
    elif datei == "frei_objekt":
        from . import frei_objekt as _datei
    elif datei == "freie_bilder":
        from . import freie_bilder as _datei
    elif datei == "freiform":
        from . import freiform as _datei
    elif datei == "geometrie":
        from . import geometrie as _datei
    elif datei == "linie":
        from . import linie as _datei
    elif datei == "muster":
        from . import muster as _datei
    elif datei == "pfad":
        from . import pfad as _datei
    elif datei == "rendering":
        from . import rendering as _datei
    elif datei == "seitenrahmen":
        from . import seitenrahmen as _datei
    elif datei == "sprechblasen":
        from . import sprechblasen as _datei
    elif datei == "textur":
        from . import textur as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
