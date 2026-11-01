"""Gemeinsame Importe, Konstanten und Hilfen für docx_writer (aus docx_writer.py herausgelöst)."""
from __future__ import annotations


import io
import logging
import os
from typing import Optional

import docx
from docx.enum.section import WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Emu, Mm, Pt, RGBColor
from PySide6.QtCore import QBuffer, QIODevice, QUrl, Qt
from PySide6.QtGui import (
    QFont, QImage, QTextBlock, QTextBlockFormat, QTextCharFormat, QTextDocument, QTextFormat,
    QTextFrame, QTextListFormat, QTextTable,
)

from lunivo_writer.models.page import PageSettings
from lunivo_writer.services.docx_teile.basis_lesen import LH_FIXED, LH_PROPORTIONAL, STYLE_PROP
from lunivo_writer.models.report import DocumentIOError, IOReport

from lunivo_writer.core.farben import Farbe
PX_TO_PT = 0.75
EMU_PER_PX = 9525

_LIST_STYLES = {
    QTextListFormat.ListDisc: "bullet", QTextListFormat.ListCircle: "bullet",
    QTextListFormat.ListSquare: "bullet", QTextListFormat.ListDecimal: "number",
    QTextListFormat.ListLowerAlpha: "number", QTextListFormat.ListUpperAlpha: "number",
    QTextListFormat.ListLowerRoman: "number", QTextListFormat.ListUpperRoman: "number",
}


def _has(fmt, prop) -> bool:
    return fmt.hasProperty(prop)


from lunivo_writer.editor.zusatz import abstand_davor_px, B_BILDANKER, B_SPALTE, P_OBJEKT, P_VERSTECKT  # noqa: E402
from lunivo_writer.editor.formular import P_FORM  # noqa: E402
from lunivo_writer.editor.abschnitte import B_ABSCHNITT  # noqa: E402
from lunivo_writer.editor import umbruch
from lunivo_writer.editor.linie import Linie, art_aus_docx, docx_wert
from lunivo_writer.editor import muster
from lunivo_writer.editor.zusatz import B_ART, B_CAP, B_MUSTER, B_RAHMEN, B_TOC, P_AENDERUNG, P_AUTOR, P_DATUM, P_FELD, P_INDEX, P_KOMMENTAR, P_NOTE


_RPR_FOLGE = ("w:rStyle", "w:rFonts", "w:b", "w:bCs", "w:i", "w:iCs", "w:caps", "w:smallCaps", "w:strike", "w:dstrike", "w:outline", "w:shadow",
              "w:emboss", "w:imprint", "w:noProof", "w:snapToGrid", "w:vanish", "w:webHidden", "w:color", "w:spacing", "w:w", "w:kern", "w:position",
              "w:sz", "w:szCs", "w:highlight", "w:u", "w:effect", "w:bdr", "w:shd", "w:fitText", "w:vertAlign", "w:rtl", "w:cs", "w:em", "w:lang",
              "w:eastAsianLayout", "w:specVanish", "w:oMath")


def _rpr_einfuegen(rpr, el) -> None:
    """Ein Element an ``w:rPr`` in der Reihenfolge einfügen, die das Schema verlangt."""
    tag = el.tag
    namen = [qn(t) for t in _RPR_FOLGE]
    nach = _RPR_FOLGE[namen.index(tag) + 1:] if tag in namen else ()
    rpr.insert_element_before(el, *nach)


def absatzopt_prop():
    from lunivo_writer.editor.zusatz import B_ABSATZOPT
    return B_ABSATZOPT


def _split(text: str):
    buf = ""
    for ch in text:
        if ch in ("\t", " ", "￼", "\n"):
            if buf:
                yield buf, "text"
                buf = ""
            yield "", {"\t": "tab", " ": "br", "\n": "br", "￼": "img"}[ch]
        else:
            buf += ch
    if buf:
        yield buf, "text"


def _rstyle_hyperlink(d):
    el = OxmlElement("w:rStyle")
    el.set(qn("w:val"), "Hyperlink")
    try:
        d.styles["Hyperlink"]
    except KeyError:
        st = d.styles.add_style("Hyperlink", WD_STYLE_TYPE.CHARACTER)
        st.font.underline = True
        st.font.color.rgb = RGBColor(0x05, 0x63, 0xC1)
    return el


class _Body:
    def __init__(self, d):
        self.d = d

    def add_paragraph(self):
        return self.d.add_paragraph()

    def add_table(self, r, c):
        return self.d.add_table(rows=r, cols=c)


class _CellBox:
    def __init__(self, cell):
        self.cell = cell

    def first_paragraph(self):
        return self.cell.paragraphs[0]

    def add_paragraph(self):
        return self.cell.add_paragraph()

    def add_table(self, r, c):
        return self.cell.add_table(r, c)
