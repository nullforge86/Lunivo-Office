"""ODT-Stilauflösung und Umsetzung von Zeichen- und Absatzformaten."""
from __future__ import annotations

import xml.etree.ElementTree as ET

from PySide6.QtCore import Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QTextBlockFormat, QTextCharFormat, QTextFormat)

from lunivo_writer.services.odt_xml import _q, _px, _pt, _kurz


class _Stile:
    """Vorlagen und automatische Formate mit Vererbung (style:parent-style-name) und Standardformat je Familie."""

    def __init__(self):
        self.stile: dict[tuple[str, str], ET.Element] = {}
        self.standard: dict[str, ET.Element] = {}
        self.listen: dict[str, ET.Element] = {}
        self.schriften: dict[str, str] = {}
        self.seiten: dict[str, ET.Element] = {}
        self._cache: dict[tuple, dict] = {}

    def lesen(self, wurzel: ET.Element | None) -> None:
        if wurzel is None:
            return
        for fd in wurzel.iter(_q("style:font-face")):
            fam = (fd.get(_q("svg:font-family")) or fd.get(_q("style:name")) or "").strip("'\"")
            self.schriften[fd.get(_q("style:name"), "")] = fam
        for bereich in ("office:styles", "office:automatic-styles"):
            b = wurzel.find(_q(bereich))
            if b is None:
                continue
            for s in b:
                if s.tag == _q("style:style"):
                    self.stile[(s.get(_q("style:family"), ""), s.get(_q("style:name"), ""))] = s
                elif s.tag == _q("style:default-style"):
                    self.standard[s.get(_q("style:family"), "")] = s
                elif s.tag == _q("text:list-style"):
                    self.listen[s.get(_q("style:name"), "")] = s
                elif s.tag == _q("style:page-layout"):
                    self.seiten[s.get(_q("style:name"), "")] = s

    def eigenschaften(self, familie: str, name: str | None, art: str) -> dict[str, str]:
        """Aufgelöste Eigenschaften (lokale Attributnamen mit Präfix, z. B. „fo:font-weight“) aus `style:<art>-properties`."""
        schluessel = (familie, name, art)
        if schluessel in self._cache:
            return self._cache[schluessel]
        kette, gesehen = [], set()
        while name and (familie, name) in self.stile and name not in gesehen:
            gesehen.add(name)
            s = self.stile[(familie, name)]
            kette.append(s)
            name = s.get(_q("style:parent-style-name"))
        if familie in self.standard:
            kette.append(self.standard[familie])
        werte: dict[str, str] = {}
        for s in reversed(kette):
            p = s.find(_q(f"style:{art}-properties"))
            if p is not None:
                for k, v in p.attrib.items():
                    werte[_kurz(k)] = v
        self._cache[schluessel] = werte
        return werte

    def liste_von(self, absatz_stil: str | None) -> str | None:
        while absatz_stil and ("paragraph", absatz_stil) in self.stile:
            s = self.stile[("paragraph", absatz_stil)]
            if s.get(_q("style:list-style-name")):
                return s.get(_q("style:list-style-name"))
            absatz_stil = s.get(_q("style:parent-style-name"))
        return None



def _zeichenformat(p: dict[str, str], stile: _Stile) -> QTextCharFormat:
    cf = QTextCharFormat()
    name = stile.schriften.get(p.get("style:font-name", ""), "") or p.get("fo:font-family", "").strip("'\"")
    if name:
        cf.setFontFamilies([name])
    groesse = _pt(p.get("fo:font-size"))
    if groesse:
        cf.setFontPointSize(groesse)
    if p.get("fo:font-weight") in ("bold", "600", "700", "800", "900"):
        cf.setFontWeight(QFont.Bold)
    elif p.get("fo:font-weight") == "normal":
        cf.setFontWeight(QFont.Normal)
    if "fo:font-style" in p:
        cf.setFontItalic(p["fo:font-style"] in ("italic", "oblique"))
    if "style:text-underline-style" in p:
        cf.setFontUnderline(p["style:text-underline-style"] != "none")
    if "style:text-line-through-style" in p:
        cf.setFontStrikeOut(p["style:text-line-through-style"] != "none")
    pos = p.get("style:text-position", "").split()
    if pos:
        if pos[0] == "super" or (pos[0].rstrip("%").lstrip("-").replace(".", "").isdigit() and not pos[0].startswith("-")
                                 and pos[0].rstrip("%") not in ("0", "0.0")):
            cf.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        elif pos[0] == "sub" or pos[0].startswith("-"):
            cf.setVerticalAlignment(QTextCharFormat.AlignSubScript)
    farbe = p.get("fo:color")
    if farbe and QColor(farbe).isValid():
        cf.setForeground(QBrush(QColor(farbe)))
    hg = p.get("fo:background-color")
    if hg and hg != "transparent" and QColor(hg).isValid():
        cf.setBackground(QBrush(QColor(hg)))
    return cf


def _absatzformat(p: dict[str, str]) -> QTextBlockFormat:
    bf = QTextBlockFormat()
    ausr = {"start": Qt.AlignLeft, "left": Qt.AlignLeft, "center": Qt.AlignHCenter, "end": Qt.AlignRight, "right": Qt.AlignRight,
            "justify": Qt.AlignJustify}.get(p.get("fo:text-align", ""))
    if ausr is not None:
        bf.setAlignment(ausr)
    for attr, setzen in (("fo:margin-left", bf.setLeftMargin), ("fo:margin-right", bf.setRightMargin),
                         ("fo:margin-top", bf.setTopMargin), ("fo:margin-bottom", bf.setBottomMargin),
                         ("fo:text-indent", bf.setTextIndent)):
        if attr in p and not p[attr].endswith("%"):
            setzen(_px(p[attr]))
    if p.get("fo:break-before") == "page":
        bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
    return bf

