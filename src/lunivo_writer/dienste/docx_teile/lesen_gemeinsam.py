"""DOCX lesen — gemeinsame Bausteine (Importe, Konstanten, Hilfsfunktionen), von allen Teilen benutzt. Nichts hängt hier von den Teilen ab."""
# ruff: noqa: F401   (Sammelstelle: die Teile und docx_leser holen sich ihre Namen von hier)
from __future__ import annotations

import io

import logging

import zipfile

from typing import Optional

import docx

from docx.document import Document as _Document

from docx.enum.style import WD_STYLE_TYPE

from docx.enum.text import WD_ALIGN_PARAGRAPH

from docx.oxml.ns import qn

from docx.table import Table

from docx.text.hyperlink import Hyperlink

from docx.text.run import Run

from docx.text.paragraph import Paragraph

from PySide6.QtCore import QUrl

from PySide6.QtGui import (
    QBrush, QColor, QFont, QImage, QTextBlockFormat, QTextCharFormat,
    QTextCursor, QTextDocument, QTextFormat, QTextFrameFormat, QTextImageFormat,
    QTextLength, QTextListFormat, QTextTableFormat,
)

from lunivo_writer.modelle.seite import HeaderFooter, PageSettings, mm_to_px, px_to_mm

from lunivo_writer.modelle.bericht import DocumentIOError, IOReport

LH_PROPORTIONAL, LH_FIXED, LH_MIN = 1, 2, 3     # QTextBlockFormat.LineHeightTypes (MinimumHeight: w:lineRule="atLeast")

from lunivo_writer.kern.farben import Farbe

STYLE_PROP = QTextFormat.UserProperty + 1       # Name der Formatvorlage am Block

from lunivo_writer.editor.dokument.zusatz import B_SPALTE, P_DEKORATIV, P_OBJEKT, P_VERSTECKT  # noqa: E402

from lunivo_writer.editor.dokument.formular import P_FORM  # noqa: E402

from lunivo_writer.editor.objekte.linie import Linie, art_aus_docx, docx_wert

from lunivo_writer.editor.text import muster

from lunivo_writer.editor.dokument.zusatz import B_ART, B_CAP, B_MUSTER, B_RAHMEN, B_TOC, BESCHRIFTUNGEN, P_AENDERUNG, P_AUTOR, P_DATUM, P_FELD, P_INDEX, P_KOMMENTAR, P_NOTE, P_ZITAT, leere_meta

EMU_PER_PX = 9525

PT_PER_PX = 0.75

HEADING_DEFAULT_PT = {1: 20, 2: 16, 3: 14, 4: 12, 5: 11, 6: 11, 7: 11, 8: 11, 9: 11}

NAMED_STYLE_DEFAULT = {  # Name → (Punktgröße, fett, kursiv)
    "Title": (26, False, False),
    "Subtitle": (15, False, True),
    "Quote": (None, False, True),
}

from PySide6.QtCore import Qt  # noqa: E402

_QT_ALIGN = {
    WD_ALIGN_PARAGRAPH.LEFT: Qt.AlignLeft,
    WD_ALIGN_PARAGRAPH.CENTER: Qt.AlignHCenter,
    WD_ALIGN_PARAGRAPH.RIGHT: Qt.AlignRight,
    WD_ALIGN_PARAGRAPH.JUSTIFY: Qt.AlignJustify,
}

# Was beim Lesen nicht übernommen wird → Hinweis
_MC_ALT = "{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent"

_MC_CHOICE = "{http://schemas.openxmlformats.org/markup-compatibility/2006}Choice"

_UNSUPPORTED = [
    ("//w:txbxContent[not(ancestor::wps:wsp[wps:txbx or wps:linkedTxbx]) and not(ancestor::v:shape) and not(ancestor::mc:Fallback)]", "Textfelder werden nicht dargestellt und gehen beim Speichern verloren."),
    ("//m:oMath", "Formeln werden nicht dargestellt und gehen beim Speichern verloren."),
    ("//w:pict[not(ancestor::mc:Fallback) and not(.//v:shape[v:textbox or v:imagedata or @id] | .//v:rect | .//v:oval | .//v:roundrect)] | //wps:wsp[not(.//a:blip) and not(wps:txbx or wps:linkedTxbx) and not(wps:spPr/a:prstGeom[@prst] or wps:spPr/a:custGeom)]",
     "Formen und gezeichnete Objekte werden nicht dargestellt."),
    ("//w:drawing[.//wp:anchor[.//wp:wrapTopAndBottom]]",
     "Bilder mit „Oben und unten“-Umbruch werden als Bild im Text eingefügt."),
]

from docx.oxml.ns import nsmap as _NS_DOCX  # noqa: E402

_WPS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"

_NS = {**_NS_DOCX, "wps": _WPS, "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
       "v": "urn:schemas-microsoft-com:vml", "o": "urn:schemas-microsoft-com:office:office",
       "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"}

def _xp(el, ausdruck: str):
    """XPath mit den Namensräumen von python-docx — auch für Elemente, deren Klasse kein eigenes xpath mit Namensräumen hat."""
    from lxml import etree
    return etree._Element.xpath(el, ausdruck, namespaces=_NS)

def _emu_to_px(v) -> float:
    return float(v) / EMU_PER_PX if v is not None else 0.0

def _pt_to_px(v) -> float:
    return float(v) / PT_PER_PX

from lunivo_writer.dienste.import_grenzen import lxml_parser  # noqa: E402

def _style_chain(style):
    seen = set()
    while style is not None and id(style) not in seen:
        seen.add(id(style))
        yield style
        style = style.base_style

def _doc_defaults(document: _Document) -> tuple[Optional[str], Optional[float]]:
    name, size = None, None
    styles = document.styles.element
    rpr = styles.find(qn("w:docDefaults") + "/" + qn("w:rPrDefault") + "/" + qn("w:rPr"))
    if rpr is not None:
        f = rpr.find(qn("w:rFonts"))
        if f is not None:
            name = f.get(qn("w:ascii"))
        s = rpr.find(qn("w:sz"))
        if s is not None:
            size = int(s.get(qn("w:val"))) / 2.0
    return name, size

class _NoRun:
    """Platzhalter, um Absatz-Standardwerte ohne Run aufzulösen."""
    class _F:
        name = None
        size = None
        bold = italic = underline = strike = superscript = subscript = None
        all_caps = small_caps = outline = hidden = None
        color = None
    font = _F()
    style = None

_ERSATZ = {"Calibri Light": ["Carlito"], "Calibri": ["Carlito"], "Cambria": ["Caladea"], "Segoe UI": ["Noto Sans"]}
