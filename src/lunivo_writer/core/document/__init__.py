"""Dokumentenmodell ohne Qt.

Maßgeblich ist das Modell aus ``dokument.py`` (``Dokument``, ``Absatz``, ``Lauf`` …). Die englisch benannten Klassen aus ``model.py``
(``Document``, ``Paragraph`` …) gehören zum bisherigen Qt-Adapter-Kern und entfallen, sobald ihre Aufrufstellen umgestellt sind.
"""
from .dokument import (
    Absatz, Abschnitt, Auswahl, Dokument, Formatvorlage, FreiesObjekt, InlineObjekt, Kommentar, Lauf, ListenDefinition, ListenEbene, Note,
    Position, Rahmen, Tabelle, Zelle, neues_dokument,
)
from .formate import FormatFehler
from .model import (Block, CharacterFormat, Document, Footnote, Frame, Image, ListFormat, PageLayout, Paragraph, ParagraphFormat,
                                               Run, Section, Table, TableCell, TableRow, TextRun)
from .pruefung import pruefe_dokument
from .serialisierung import dokument_aus_daten, dokument_zu_daten
from .values import Brush, Color, GradientBrush, Length, LineSpacing, Pen, PropertyValue, RowHeight, TabStop, TextureBrush

__all__ = ["Absatz", "Abschnitt", "Auswahl", "Dokument", "FormatFehler", "Formatvorlage", "FreiesObjekt", "InlineObjekt", "Kommentar", "Lauf",
           "ListenDefinition", "ListenEbene", "Note", "Position", "Rahmen", "Tabelle", "Zelle", "dokument_aus_daten", "dokument_zu_daten",
           "neues_dokument", "pruefe_dokument",
           "Block", "Brush", "CharacterFormat", "Color", "Document", "Footnote", "Frame", "GradientBrush", "Image", "Length", "PageLayout", "Pen", "TextureBrush", "ListFormat", "Paragraph", "ParagraphFormat",
           "LineSpacing", "PropertyValue", "RowHeight", "Run", "Section", "Table", "TableCell", "TableRow", "TabStop", "TextRun"]
