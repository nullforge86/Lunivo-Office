"""Tür des Pakets ``framework.befehle.ansicht``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AUGENSCHUTZ": ("einstellungen", "AUGENSCHUTZ"),
    "AnsichtBefehle": ("befehle", "AnsichtBefehle"),
    "Anzeige": ("seitenbilder", "Anzeige"),
    "Blattangabe": ("layout", "Blattangabe"),
    "GLIEDERUNG_AN": ("befehle", "GLIEDERUNG_AN"),
    "GLIEDERUNG_AUS": ("befehle", "GLIEDERUNG_AUS"),
    "LINEAL": ("einstellungen", "LINEAL"),
    "LINEAL_HOCH": ("einstellungen", "LINEAL_HOCH"),
    "OBERFLAECHE": ("einstellungen", "OBERFLAECHE"),
    "OBERFLAECHE_SCHLUESSEL": ("einstellungen", "OBERFLAECHE_SCHLUESSEL"),
    "Platzangabe": ("layout", "Platzangabe"),
    "SILBEN_AN": ("lesehilfe", "SILBEN_AN"),
    "Seitenangabe": ("layout", "Seitenangabe"),
    "THEMA": ("einstellungen", "THEMA"),
    "VERSTECKT_ZEIGEN": ("einstellungen", "VERSTECKT_ZEIGEN"),
    "VORGABEN": ("einstellungen", "VORGABEN"),
    "WEICH": ("einstellungen", "WEICH"),
    "aktiv": ("sprechblasen", "aktiv"),
    "augenschutz_an": ("einstellungen", "augenschutz_an"),
    "augenschutz_umschalten": ("einstellungen", "augenschutz_umschalten"),
    "ausgabe_als_pdf": ("ausgabe", "ausgabe_als_pdf"),
    "ausgabe_anzahl": ("ausgabe", "ausgabe_anzahl"),
    "ausgabe_aus_datei": ("ausgabe", "ausgabe_aus_datei"),
    "ausgabe_aus_geruest": ("ausgabe", "ausgabe_aus_geruest"),
    "ausgabe_blasen": ("ausgabe", "ausgabe_blasen"),
    "ausgabe_oeffnen": ("ausgabe", "ausgabe_oeffnen"),
    "ausgabe_schliessen": ("ausgabe", "ausgabe_schliessen"),
    "ausgabe_seite_mm": ("ausgabe", "ausgabe_seite_mm"),
    "ausgabe_seitenbild": ("ausgabe", "ausgabe_seitenbild"),
    "blasen_px": ("sprechblasen", "blasen_px"),
    "blasen_schrift": ("sprechblasen", "blasen_schrift"),
    "breite_mm": ("sprechblasen", "breite_mm"),
    "cursorbild": ("seitenbilder", "cursorbild"),
    "einstellung_lesen": ("silbenfarben", "einstellung_lesen"),
    "einstellung_speichern": ("silbenfarben", "einstellung_speichern"),
    "farben": ("silbenfarben", "farben"),
    "fuer_den_druck": ("silbenfarben", "fuer_den_druck"),
    "karten_pt": ("sprechblasen", "karten_pt"),
    "konfig_lesen": ("sprechblasen", "konfig_lesen"),
    "layout_berechnen": ("layout", "berechnen"),
    "layout_bewegen": ("layout", "bewegen"),
    "layout_blattmasse": ("layout", "blattmasse"),
    "layout_cursor": ("layout", "cursor"),
    "layout_cursor_rechteck": ("layout", "cursor_rechteck"),
    "layout_objekt_bei": ("layout", "objekt_bei"),
    "layout_objekte": ("layout", "objekte"),
    "layout_option_setzen": ("layout", "option_setzen"),
    "layout_reihenfolge": ("layout", "reihenfolge"),
    "layout_seite": ("layout", "seite"),
    "layout_seite_von": ("layout", "seite_von"),
    "layout_seitenzahl": ("layout", "seitenzahl"),
    "layout_silben_setzen": ("layout", "silben_setzen"),
    "layout_treffer": ("layout", "treffer"),
    "layout_verwerfen": ("layout", "verwerfen"),
    "layout_wort_bei": ("layout", "wort_bei"),
    "lineal_hoch_umschalten": ("einstellungen", "lineal_hoch_umschalten"),
    "lineal_hoch_zeigen": ("einstellungen", "lineal_hoch_zeigen"),
    "lineal_umschalten": ("einstellungen", "lineal_umschalten"),
    "lineal_zeigen": ("einstellungen", "lineal_zeigen"),
    "messen": ("sprechblasen", "messen"),
    "neue_einstellung": ("silbenfarben", "neue_einstellung"),
    "oberflaeche_umschalten": ("einstellungen", "oberflaeche_umschalten"),
    "oberflaeche_zuruecksetzen": ("einstellungen", "oberflaeche_zuruecksetzen"),
    "ortszeit": ("sprechblasen", "ortszeit"),
    "sammeln": ("sprechblasen", "sammeln"),
    "seitenbild": ("seitenbilder", "seitenbild"),
    "silben": ("silbenfarben", "silben"),
    "silben_an": ("lesehilfe", "silben_an"),
    "silben_umschalten": ("lesehilfe", "silben_umschalten"),
    "silbenfarben_katalog": ("silbenfarben", "katalog"),
    "sprechblasen_katalog": ("sprechblasen", "katalog"),
    "stapeln": ("sprechblasen", "stapeln"),
    "symbolleisten_statt_register": ("einstellungen", "symbolleisten_statt_register"),
    "thema": ("einstellungen", "thema"),
    "ueberlagerung_setzen": ("seitenbilder", "ueberlagerung_setzen"),
    "ueberlagerung_stand": ("seitenbilder", "ueberlagerung_stand"),
    "ueberlagerungsbild": ("seitenbilder", "ueberlagerungsbild"),
    "verstecktes_umschalten": ("einstellungen", "verstecktes_umschalten"),
    "verstecktes_zeigen": ("einstellungen", "verstecktes_zeigen"),
    "vorlagen_ordner": ("vorlagen", "vorlagen_ordner"),
    "vorlagen_ordner_pfad": ("vorlagen", "vorlagen_ordner_pfad"),
    "vorschau_brief": ("vorschau", "vorschau_brief"),
    "vorschau_kopie": ("vorschau", "vorschau_kopie"),
    "vorschau_schliessen": ("vorschau", "vorschau_schliessen"),
    "weich": ("einstellungen", "weich"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "befehle":
        from . import befehle as _datei
    elif datei == "einstellungen":
        from . import einstellungen as _datei
    elif datei == "ausgabe":
        from . import ausgabe as _datei
    elif datei == "layout":
        from . import layout as _datei
    elif datei == "seitenbilder":
        from . import seitenbilder as _datei
    elif datei == "lesehilfe":
        from . import lesehilfe as _datei
    elif datei == "silbenfarben":
        from . import silbenfarben as _datei
    elif datei == "sprechblasen":
        from . import sprechblasen as _datei
    elif datei == "vorschau":
        from . import vorschau as _datei
    elif datei == "vorlagen":
        from . import vorlagen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
