"""Dokumentenmodell ohne Qt.

Maßgeblich ist das Modell aus ``dokument.py`` (``Dokument``, ``Absatz``, ``Lauf`` …); ein zweites Modell gibt es nicht. ``values.py`` hält Wertetypen (Farben,
Längen, Pinsel), die Leser beim Umrechnen von Stilangaben benutzen.
"""
from core.dokument.dokument import Absatz, Abschnitt, Auswahl, Dokument, Formatvorlage, FreiesObjekt, InlineObjekt, Kommentar, Lauf, ListenDefinition, ListenEbene, Note, Position, Rahmen, Tabelle, Zelle, absaetze_in, neues_dokument, teile
from core.dokument.formate import FormatFehler
from core.dokument.pruefung import pruefe_dokument
from core.dokument.serialisierung import dokument_aus_daten, dokument_zu_daten
from core.dokument.values import Brush, Color, GradientBrush, Length, LineSpacing, Pen, PropertyValue, RowHeight, TabStop, TextureBrush

__all__ = ["absaetze_in", "teile", "Absatz", "Abschnitt", "Auswahl", "Dokument", "FormatFehler", "Formatvorlage", "FreiesObjekt", "InlineObjekt", "Kommentar", "Lauf",
           "ListenDefinition", "ListenEbene", "Note", "Position", "Rahmen", "Tabelle", "Zelle", "dokument_aus_daten", "dokument_zu_daten",
           "neues_dokument", "pruefe_dokument",
           "Brush", "Color", "GradientBrush", "Length", "LineSpacing", "Pen", "PropertyValue", "RowHeight", "TabStop", "TextureBrush",
           "GEHE_ZU_EINGABE", "GEHE_ZU_ELEMENTE", "gehe_zu_positionen", "gehe_zu_springen", "gehe_zu_ziel",
           "ANGABE_FELDER", "angabe_von", "felder_aus_angabe"]

# Erst beim ersten Zugriff geladen: „Gehe zu“ braucht Verweise und Verzeichnisse, die ihrerseits das Dokumentenmodell laden.
_SPAET: dict[str, tuple[str, str]] = {"GEHE_ZU_EINGABE": ("gehe_zu", "EINGABE"), "GEHE_ZU_ELEMENTE": ("gehe_zu", "ELEMENTE"),
                                      "gehe_zu_positionen": ("gehe_zu", "positionen"), "gehe_zu_springen": ("gehe_zu", "springen"),
                                      "gehe_zu_ziel": ("gehe_zu", "ziel"), "ANGABE_FELDER": ("objekt_angabe", "ANGABE_FELDER"),
                                      "angabe_von": ("objekt_angabe", "angabe_von"), "felder_aus_angabe": ("objekt_angabe", "felder_aus_angabe")}


def __getattr__(name: str):
    datei, original = _SPAET.get(name, (None, None))
    if datei == "gehe_zu":
        from . import gehe_zu as _datei
    elif datei == "objekt_angabe":
        from . import objekt_angabe as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert
