"""ODT-Stilauflösung und Umsetzung von Zeichen- und Absatzformaten."""
from __future__ import annotations

import xml.etree.ElementTree as ET

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QFont, QTextBlockFormat, QTextCharFormat, QTextFormat

from lunivo_writer.dienste.odt_xml import _q, _px, _pt, _kurz


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
                self._eintragen(s)

    def _eintragen(self, s: ET.Element) -> None:
        """Ein Kind von ``office:styles``/``office:automatic-styles`` in die passende Tabelle legen."""
        familie, name = s.get(_q("style:family"), ""), s.get(_q("style:name"), "")
        if s.tag == _q("style:style"):
            self.stile[(familie, name)] = s
        elif s.tag == _q("style:default-style"):
            self.standard[familie] = s
        elif s.tag == _q("text:list-style"):
            self.listen[name] = s
        elif s.tag == _q("style:page-layout"):
            self.seiten[name] = s

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



_FETT = ("bold", "600", "700", "800", "900")


def _lage(pos: list[str]):
    """``style:text-position`` (z. B. „super 58%“, „-33%“) → hoch-/tiefgestellt oder ``None``."""
    if not pos:
        return None
    erste = pos[0]
    if erste == "super" or (erste.rstrip("%").lstrip("-").replace(".", "").isdigit() and not erste.startswith("-")
                            and erste.rstrip("%") not in ("0", "0.0")):
        return QTextCharFormat.AlignSuperScript
    if erste == "sub" or erste.startswith("-"):
        return QTextCharFormat.AlignSubScript
    return None


def _farbe(wert: str | None, transparent_ok: bool = True) -> QBrush | None:
    """Farbwert → Pinsel; ``None`` bei leerem, ungültigem (oder, wenn nicht erlaubt, „transparent“) Wert."""
    if not wert or (not transparent_ok and wert == "transparent") or not QColor(wert).isValid():
        return None
    return QBrush(QColor(wert))


def _schrift(cf: QTextCharFormat, p: dict[str, str], stile: _Stile) -> None:
    name = stile.schriften.get(p.get("style:font-name", ""), "") or p.get("fo:font-family", "").strip("'\"")
    if name:
        cf.setFontFamilies([name])
    groesse = _pt(p.get("fo:font-size"))
    if groesse:
        cf.setFontPointSize(groesse)
    if p.get("fo:font-weight") in _FETT:
        cf.setFontWeight(QFont.Bold)
    elif p.get("fo:font-weight") == "normal":
        cf.setFontWeight(QFont.Normal)
    if "fo:font-style" in p:
        cf.setFontItalic(p["fo:font-style"] in ("italic", "oblique"))


def _zeichenformat(p: dict[str, str], stile: _Stile) -> QTextCharFormat:
    cf = QTextCharFormat()
    _schrift(cf, p, stile)
    if "style:text-underline-style" in p:
        cf.setFontUnderline(p["style:text-underline-style"] != "none")
    if "style:text-line-through-style" in p:
        cf.setFontStrikeOut(p["style:text-line-through-style"] != "none")
    lage = _lage(p.get("style:text-position", "").split())
    if lage is not None:
        cf.setVerticalAlignment(lage)
    vorn = _farbe(p.get("fo:color"))
    if vorn is not None:
        cf.setForeground(vorn)
    hinten = _farbe(p.get("fo:background-color"), transparent_ok=False)
    if hinten is not None:
        cf.setBackground(hinten)
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

