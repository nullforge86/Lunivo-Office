"""Das Dokumentenmodell ohne Qt: Abschnitte mit Seiteneinrichtung, Absätze mit Textstücken, Tabellen, Bilder, Rahmen, Fußnoten.

Formate sind benannte Eigenschaften (``properties``: Name → Wert, Werte siehe ``values.py``). Benannt wird nach der Eigenschaft des Formats (zum Beispiel
``FontWeight``, ``BlockAlignment``); Eigenschaften, die Lunivo selbst anlegt (Notenmarken, Änderungen, Abschnittsdaten, Effekte …), heißen ``user:<Zahl>``.
Das Modell lässt keine Eigenschaft fallen: was ein Format trägt, steht in ``properties``. Eine Zuordnung zu fachlichen Namen (fett, Schriftgröße …) folgt in
einer späteren Phase; bis dahin liest und schreibt der Qt-Adapter (``adapter/qt/dokument.py``) diese Namen verlustfrei."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union

from lunivo_writer.core.document.values import PropertyValue


@dataclass
class CharacterFormat:
    properties: dict[str, PropertyValue] = field(default_factory=dict)

    def get(self, name: str, default: PropertyValue = None) -> PropertyValue:
        return self.properties.get(name, default)


@dataclass
class ParagraphFormat:
    properties: dict[str, PropertyValue] = field(default_factory=dict)
    char_format: CharacterFormat = field(default_factory=CharacterFormat)     # Format am Absatzende und für einen leeren Absatz
    list_id: int | None = None                                                # Zugehörigkeit zu einer Liste (``Document.lists``), None: keine
    visible: bool = True


@dataclass
class ListFormat:
    properties: dict[str, PropertyValue] = field(default_factory=dict)


@dataclass
class TextRun:
    text: str
    format: CharacterFormat = field(default_factory=CharacterFormat)


@dataclass
class Image:
    """Ein Bild in der Zeile. ``raster_png`` ist die Rasterfassung (PNG, verlustfrei); ``original`` die Originalbytes (zum Beispiel JPEG, SVG, EMF), falls vorhanden.
    ``format`` trägt die Eigenschaften des Bildes (Name, Breite, Höhe, Zeichenformat) wie ein Textstück."""
    raster_png: bytes
    format: CharacterFormat = field(default_factory=CharacterFormat)
    original: bytes | None = None
    original_format: str | None = None
    fallback_png: bytes | None = None                                         # Ersatzgrafik zu einem Vektorbild
    raster_only: bool = False


Run = Union[TextRun, Image]


@dataclass
class Paragraph:
    format: ParagraphFormat = field(default_factory=ParagraphFormat)
    runs: list[Run] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(r.text if isinstance(r, TextRun) else "￼" for r in self.runs)


@dataclass
class TableCell:
    row: int
    column: int
    row_span: int = 1
    column_span: int = 1
    properties: dict[str, PropertyValue] = field(default_factory=dict)         # Zellformat
    content: list["Block"] = field(default_factory=list)


@dataclass
class TableRow:
    cells: list[TableCell] = field(default_factory=list)                       # nur Zellen, die in dieser Zeile beginnen (verbundene Zellen stehen einmal)


@dataclass
class Table:
    rows: int
    columns: int
    properties: dict[str, PropertyValue] = field(default_factory=dict)         # Tabellenformat (Rahmen, Breiten, Spaltenvorgaben, Kopfzeilen …)
    table_rows: list[TableRow] = field(default_factory=list)


@dataclass
class Frame:
    """Ein Rahmen im Text (zum Beispiel ein schwebendes Bild mit Textumfluss)."""
    properties: dict[str, PropertyValue] = field(default_factory=dict)
    content: list["Block"] = field(default_factory=list)


Block = Union[Paragraph, Table, Frame]


@dataclass
class Footnote:
    """Fuß- oder Endnote: ``kind`` ist ``f`` oder ``e``; im Text steht die Marke als Eigenschaft des Textstücks."""
    id: int
    kind: str
    text: str


@dataclass
class Section:
    """Ein Abschnitt: wie er beginnt (``next_page``, ``continuous``, ``even_page``, ``odd_page``) und seine Seiteneinrichtung (``lunivo_writer.modelle.seite.PageSettings``)."""
    kind: str = "naechste"
    page: object = None
    content: list[Block] = field(default_factory=list)


@dataclass
class Document:
    sections: list[Section] = field(default_factory=list)
    default_format: CharacterFormat = field(default_factory=CharacterFormat)  # Grundschrift des Dokuments
    document_margin: float = 0.0
    indent_width: float = 40.0
    root_properties: dict[str, PropertyValue] = field(default_factory=dict)   # Format des Wurzelrahmens
    text_option: dict[str, PropertyValue] = field(default_factory=dict)       # Grundeinstellung des Textsatzes: Tabstoppabstand, Umbruchart, Ausrichtung, Richtung, Marken, Tabs
    lists: dict[int, ListFormat] = field(default_factory=dict)
    notes: list[Footnote] = field(default_factory=list)
    media: dict[str, "Image"] = field(default_factory=dict)                    # Bilder, auf die nur ein Name verweist (frei positionierte Bilder, Füllbilder): Name → Bild
