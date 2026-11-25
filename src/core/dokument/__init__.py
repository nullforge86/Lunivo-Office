"""Dokumentenmodell ohne Qt.

Maßgeblich ist das Modell aus ``dokument.py`` (``Dokument``, ``Absatz``, ``Lauf`` …); ein zweites Modell gibt es nicht. ``values.py`` hält Wertetypen (Farben,
Längen, Pinsel), die Leser beim Umrechnen von Stilangaben benutzen.
"""
from core.dokument.dokument import Absatz, Abschnitt, Auswahl, Dokument, Formatvorlage, FreiesObjekt, InlineObjekt, Kommentar, Lauf, ListenDefinition, ListenEbene, Note, Position, Rahmen, Tabelle, Zelle, neues_dokument, teile
from core.dokument.formate import FormatFehler
from core.dokument.pruefung import pruefe_dokument
from core.dokument.serialisierung import dokument_aus_daten, dokument_zu_daten
from core.dokument.values import Brush, Color, GradientBrush, Length, LineSpacing, Pen, PropertyValue, RowHeight, TabStop, TextureBrush

__all__ = ["teile", "Absatz", "Abschnitt", "Auswahl", "Dokument", "FormatFehler", "Formatvorlage", "FreiesObjekt", "InlineObjekt", "Kommentar", "Lauf",
           "ListenDefinition", "ListenEbene", "Note", "Position", "Rahmen", "Tabelle", "Zelle", "dokument_aus_daten", "dokument_zu_daten",
           "neues_dokument", "pruefe_dokument",
           "Brush", "Color", "GradientBrush", "Length", "LineSpacing", "Pen", "PropertyValue", "RowHeight", "TabStop", "TextureBrush",
           "GEHE_ZU_EINGABE", "GEHE_ZU_ELEMENTE", "gehe_zu_positionen", "gehe_zu_springen", "gehe_zu_ziel"]

# „Gehe zu“ lädt erst beim ersten Zugriff (braucht Verweise und Verzeichnisse, die ihrerseits das Dokumentenmodell laden).
_SPAET: dict[str, str] = {"GEHE_ZU_EINGABE": "EINGABE", "GEHE_ZU_ELEMENTE": "ELEMENTE", "gehe_zu_positionen": "positionen",
                          "gehe_zu_springen": "springen", "gehe_zu_ziel": "ziel"}


def __getattr__(name: str):
    if name not in _SPAET:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    from . import gehe_zu as _datei
    wert = getattr(_datei, _SPAET[name])
    globals()[name] = wert
    return wert
