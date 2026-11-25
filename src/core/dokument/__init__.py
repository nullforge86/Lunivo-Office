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
           "Brush", "Color", "GradientBrush", "Length", "LineSpacing", "Pen", "PropertyValue", "RowHeight", "TabStop", "TextureBrush"]
