"""Tür des Pakets ``core.objekte.formen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ABSCHLUSS": ("bildeffekte_daten", "ABSCHLUSS"),
    "ALLE_SEITEN": ("linie_daten", "ALLE_SEITEN"),
    "AUSRICHTUNG": ("sprechblasen_modell", "AUSRICHTUNG"),
    "BLASE_RAND": ("sprechblasen_modell", "BLASE_RAND"),
    "BLASE_UEBERABTASTUNG": ("sprechblasen_modell", "BLASE_UEBERABTASTUNG"),
    "Blase": ("sprechblasen_modell", "Blase"),
    "EMPFOHLENE_BREITE_MM": ("sprechblasen_modell", "EMPFOHLENE_BREITE_MM"),
    "EMU_PX": ("freie_bilder_daten", "EMU_PX"),
    "GRUPPEN_ABSTAND": ("formen_daten", "GRUPPEN_ABSTAND"),
    "KOPF_HOEHE": ("sprechblasen_modell", "KOPF_HOEHE"),
    "LINIENBREITEN": ("linie_daten", "LINIENBREITEN"),
    "LUECKE_MM": ("sprechblasen_modell", "LUECKE_MM"),
    "MAX_BILDPUNKTE": ("freie_bilder_daten", "MAX_BILDPUNKTE"),
    "NEU_ZEICHNEN": ("frei_objekt_daten", "NEU_ZEICHNEN"),
    "OBJEKT_STRICHE": ("linie_daten", "OBJEKT_STRICHE"),
    "PX_PT": ("bildeffekte_daten", "PX_PT"),
    "RAND": ("sprechblasen_modell", "RAND"),
    "SCHEMA": ("freie_bilder_daten", "SCHEMA"),
    "SCHRIFTEN": ("sprechblasen_modell", "SCHRIFTEN"),
    "SPALTEN": ("formen_stile_daten", "SPALTEN"),
    "VERWENDEN": ("sprechblasen_modell", "VERWENDEN"),
    "VORGABE": ("bildeffekte_daten", "VORGABE"),
    "VORLAGEN": ("formen_daten", "VORLAGEN"),
    "ZEILEN": ("formen_stile_daten", "ZEILEN"),
    "aktiv": ("sprechblasen_modell", "aktiv"),
    "als_text": ("muster_daten", "als_text"),
    "aus_text": ("muster_daten", "aus_text"),
    "autor_farbe": ("sprechblasen_modell", "autor_farbe"),
    "blasen_px": ("sprechblasen_modell", "blasen_px"),
    "blasen_schrift": ("sprechblasen_modell", "blasen_schrift"),
    "breite_mm": ("sprechblasen_modell", "breite_mm"),
    "emu_zu_px": ("freie_bilder_daten", "emu_zu_px"),
    "form_daten": ("formen_daten", "form_daten"),
    "formen_daten_STANDARD": ("formen_daten", "STANDARD"),
    "hat_abschluss": ("bildeffekte_daten", "hat_abschluss"),
    "hat_drehung": ("bildeffekte_daten", "hat_drehung"),
    "hat_nachbearbeitung": ("bildeffekte_daten", "hat_nachbearbeitung"),
    "hat_nachfolger": ("frei_objekt_daten", "hat_nachfolger"),
    "ist_verknuepft": ("frei_objekt_daten", "ist_verknuepft"),
    "karten_pt": ("sprechblasen_modell", "karten_pt"),
    "konfig_lesen": ("sprechblasen_modell", "konfig_lesen"),
    "messen": ("sprechblasen_modell", "messen"),
    "nach_groesse": ("frei_objekt_daten", "nach_groesse"),
    "name_von": ("muster_daten", "name_von"),
    "ohne_hilfsangaben": ("freie_bilder_daten", "ohne_hilfsangaben"),
    "ooxml_von": ("muster_daten", "ooxml_von"),
    "sammeln_modell": ("sprechblasen_modell", "sammeln_modell"),
    "schluessel_von_ooxml": ("muster_daten", "schluessel_von_ooxml"),
    "sprechblasen_modell_STANDARD": ("sprechblasen_modell", "STANDARD"),
    "stapeln": ("sprechblasen_modell", "stapeln"),
    "tiefe_richtung": ("bildeffekte_daten", "tiefe_richtung"),
    "vorne_hinten": ("freie_bilder_daten", "vorne_hinten"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "bildeffekte_daten":
        from . import bildeffekte_daten as _datei
    elif datei == "formen_daten":
        from . import formen_daten as _datei
    elif datei == "formen_stile_daten":
        from . import formen_stile_daten as _datei
    elif datei == "frei_objekt_daten":
        from . import frei_objekt_daten as _datei
    elif datei == "freie_bilder_daten":
        from . import freie_bilder_daten as _datei
    elif datei == "linie_daten":
        from . import linie_daten as _datei
    elif datei == "muster_daten":
        from . import muster_daten as _datei
    elif datei == "sprechblasen_modell":
        from . import sprechblasen_modell as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
