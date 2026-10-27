"""ODT und FODT (OpenDocument-Text) direkt lesen — ohne Umwandlungsprogramm.

Gelesen werden ``content.xml`` (Text), ``styles.xml`` (Vorlagen, Seite, Kopf- und Fußzeile), ``meta.xml`` (Titel, Autor) und die Bilder
aus ``Pictures/``; FODT ist dasselbe als eine einzige XML-Datei. Übernommen: Absätze und Überschriften mit Ausrichtung, Einzügen,
Abständen und Seitenumbruch; Zeichenformat (Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen, hoch/tief, Farbe,
Hintergrund); Listen; Tabellen (auch verbundene Zellen); Bilder; Seitengröße, Seitenränder, Kopf- und Fußzeile mit Seitenzahl.
Was nicht übernommen wird (Fußnoten, Kommentare, Textrahmen, Zeichnungen), meldet der Bericht.
"""
from __future__ import annotations

import base64
import re
import zipfile
import xml.etree.ElementTree as ET

from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QImage, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument,
                           QTextFormat, QTextImageFormat, QTextLength, QTextListFormat, QTextTableFormat)

from lunivo_writer.models.page import HeaderFooter, PageSettings, px_to_mm
from lunivo_writer.models.report import DocumentIOError, IOReport

NS = {
    "office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0",
    "style": "urn:oasis:names:tc:opendocument:xmlns:style:1.0",
    "text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0",
    "table": "urn:oasis:names:tc:opendocument:xmlns:table:1.0",
    "draw": "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0",
    "fo": "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0",
    "svg": "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0",
    "xlink": "http://www.w3.org/1999/xlink",
    "dc": "http://purl.org/dc/elements/1.1/",
    "meta": "urn:oasis:names:tc:opendocument:xmlns:meta:1.0",
}
GRENZE_BYTES = 512 * 1024 * 1024          # entpackt höchstens so viel (Schutz vor „ZIP-Bomben“ und Speicherüberlauf)
MAX_WIEDERHOLUNG = 1000                   # table:number-rows/columns-repeated: leere Füllzeilen nicht ins Unendliche
_PX = {"in": 96.0, "cm": 96 / 2.54, "mm": 96 / 25.4, "pt": 96 / 72, "pc": 16.0, "px": 1.0}


def _q(name: str) -> str:
    pre, lokal = name.split(":")
    return f"{{{NS[pre]}}}{lokal}"


def _px(wert: str | None, standard: float = 0.0) -> float:
    m = re.fullmatch(r"\s*(-?[\d.]+)\s*([a-z]*)\s*", wert or "")
    if not m:
        return standard
    try:
        return float(m.group(1)) * _PX.get(m.group(2) or "px", 1.0)
    except ValueError:
        return standard


def _pt(wert: str | None) -> float | None:
    if not wert or wert.endswith("%"):
        return None
    px = _px(wert, -1)
    return px * 72 / 96 if px > 0 else None


def _text_von(el: ET.Element) -> str:
    """Reiner Text eines Elements samt Kindern (für Kopf- und Fußzeilen); Seitenzahl-Felder werden zu {PAGE}/{PAGES}."""
    teile = [el.text or ""]
    for k in el:
        if k.tag == _q("text:page-number"):
            teile.append("{PAGE}")
        elif k.tag == _q("text:page-count"):
            teile.append("{PAGES}")
        elif k.tag == _q("text:s"):
            teile.append(" " * int(k.get(_q("text:c"), "1") or 1))
        elif k.tag == _q("text:tab"):
            teile.append("\t")
        else:
            teile.append(_text_von(k))
        teile.append(k.tail or "")
    return "".join(teile)


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


_PRAEFIX = {v: k for k, v in NS.items()}


def _kurz(attr: str) -> str:
    if attr.startswith("{"):
        uri, lokal = attr[1:].split("}")
        return f"{_PRAEFIX.get(uri, '?')}:{lokal}"
    return attr


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


class _Ort:
    """Wohin der nächste Absatz kommt: ein Cursor und ob dessen Block noch leer und frei ist."""

    def __init__(self, cur: QTextCursor, frei: bool = True):
        self.cur, self.frei = cur, frei


class _Leser:
    def __init__(self, inhalt: ET.Element, stil_wurzel: ET.Element | None, meta: ET.Element | None, bilder):
        self.inhalt, self.stil_wurzel, self.meta_el, self.bilder = inhalt, stil_wurzel, meta, bilder
        self.report = IOReport()
        self.stile = _Stile()
        self.stile.lesen(stil_wurzel)
        if inhalt is not stil_wurzel:
            self.stile.lesen(inhalt)
        self.doc = QTextDocument()
        self.doc.setDocumentMargin(0)
        self.bild_n = 0

    # ---- Absätze --------------------------------------------------------------------------------------------------------
    def absatz(self, el: ET.Element, ort: _Ort, liste: tuple | None = None) -> None:
        stil = el.get(_q("text:style-name"))
        pp = self.stile.eigenschaften("paragraph", stil, "paragraph")
        tp = self.stile.eigenschaften("paragraph", stil, "text")
        bf = _absatzformat(pp)
        if el.tag == _q("text:h"):
            try:
                bf.setHeadingLevel(max(1, min(9, int(el.get(_q("text:outline-level"), "1")))))
            except ValueError:
                bf.setHeadingLevel(1)
        grund = _zeichenformat(tp, self.stile)
        if ort.frei:
            ort.cur.setBlockFormat(bf)
            ort.cur.setBlockCharFormat(grund)
            ort.frei = False
        else:
            ort.cur.insertBlock(bf, grund)
        if liste is not None:
            self.listenpunkt(ort.cur, *liste)
        self.inline(el, ort.cur, tp)

    def inline(self, el: ET.Element, cur: QTextCursor, eltern: dict[str, str]) -> None:
        cf = _zeichenformat(eltern, self.stile)
        if el.text:
            cur.insertText(el.text, cf)
        for k in el:
            t = k.tag
            if t == _q("text:span"):
                p = dict(eltern)
                p.update(self.stile.eigenschaften("text", k.get(_q("text:style-name")), "text"))
                self.inline(k, cur, p)
            elif t in (_q("text:a"), _q("text:meta"), _q("text:ruby"), _q("text:ruby-base")):
                self.inline(k, cur, eltern)
            elif t == _q("text:s"):
                try:
                    n = max(1, min(1000, int(k.get(_q("text:c"), "1"))))
                except ValueError:
                    n = 1
                cur.insertText(" " * n, cf)
            elif t == _q("text:tab"):
                cur.insertText("\t", cf)
            elif t == _q("text:line-break"):
                cur.insertText(" ", cf)
            elif t == _q("draw:frame"):
                self.rahmen(k, cur)
            elif t == _q("text:note"):
                self.report.warn("Fuß- und Endnoten aus der ODT-Datei wurden nicht übernommen.")
            elif t == _q("office:annotation"):
                self.report.warn("Kommentare aus der ODT-Datei wurden nicht übernommen.")
            elif t in (_q("office:annotation-end"), _q("text:soft-page-break"), _q("text:bookmark"), _q("text:bookmark-start"),
                       _q("text:bookmark-end"), _q("text:reference-mark"), _q("text:reference-mark-start"),
                       _q("text:reference-mark-end"), _q("text:alphabetical-index-mark"), _q("text:toc-mark"),
                       _q("text:change-start"), _q("text:change-end"), _q("text:change")):
                pass
            elif t.startswith("{" + NS["draw"]):
                self.report.warn("Zeichnungen und Formen aus der ODT-Datei wurden nicht übernommen.")
            else:                                                 # Felder (Datum, Seitenzahl …): der angezeigte Text
                self.inline(k, cur, eltern)
            if k.tail:
                cur.insertText(k.tail, cf)

    def rahmen(self, frame: ET.Element, cur: QTextCursor) -> None:
        bild = frame.find(_q("draw:image"))
        if bild is None:
            if frame.find(_q("draw:text-box")) is not None:
                self.report.warn("Textrahmen aus der ODT-Datei wurden als Text übernommen.")
                for k in frame.find(_q("draw:text-box")).iter():
                    if k.tag in (_q("text:p"), _q("text:h")):
                        cur.insertText(_text_von(k) + " ")
            else:
                self.report.warn("Zeichnungen und Formen aus der ODT-Datei wurden nicht übernommen.")
            return
        daten = None
        href = bild.get(_q("xlink:href"), "")
        binaer = bild.find(_q("office:binary-data"))
        if binaer is not None and binaer.text:
            try:
                daten = base64.b64decode(binaer.text)
            except ValueError:
                daten = None
        elif href and not re.match(r"^[a-z]+:", href):
            daten = self.bilder(href.lstrip("./"))
        img = QImage()
        if not daten or not img.loadFromData(daten):
            from lunivo_writer.editor.freie_bilder import bild_aus_daten
            img = bild_aus_daten(daten) if daten else QImage()
        if img.isNull():
            self.report.warn("Ein Bild aus der ODT-Datei war nicht lesbar und wurde übersprungen.")
            return
        self.bild_n += 1
        name = f"odt-bild-{self.bild_n}"
        self.doc.addResource(QTextDocument.ImageResource, QUrl(name), img)
        f = QTextImageFormat()
        f.setName(name)
        f.setWidth(_px(frame.get(_q("svg:width")), img.width()))
        f.setHeight(_px(frame.get(_q("svg:height")), img.height()))
        cur.insertImage(f)

    # ---- Listen ---------------------------------------------------------------------------------------------------------
    def listenpunkt(self, cur: QTextCursor, listen: dict, stil: str | None, ebene: int) -> None:
        if ebene not in listen:
            lf = QTextListFormat()
            lf.setIndent(ebene)
            lf.setStyle(self._listenart(stil, ebene))
            listen[ebene] = cur.createList(lf)
            for tiefer in [e for e in listen if e > ebene]:
                del listen[tiefer]
        else:
            listen[ebene].add(cur.block())
            for tiefer in [e for e in listen if e > ebene]:
                del listen[tiefer]

    def _listenart(self, stil: str | None, ebene: int):
        ls = self.stile.listen.get(stil or "")
        if ls is not None:
            for k in ls:
                if k.get(_q("text:level")) == str(ebene):
                    if k.tag == _q("text:list-level-style-number"):
                        return {"a": QTextListFormat.ListLowerAlpha, "A": QTextListFormat.ListUpperAlpha,
                                "i": QTextListFormat.ListLowerRoman, "I": QTextListFormat.ListUpperRoman,
                                }.get(k.get(_q("style:num-format"), "1"), QTextListFormat.ListDecimal)
                    zeichen = k.get(_q("text:bullet-char"), "•")
                    return {"◦": QTextListFormat.ListCircle, "○": QTextListFormat.ListCircle, "▪": QTextListFormat.ListSquare,
                            "■": QTextListFormat.ListSquare}.get(zeichen, QTextListFormat.ListDisc)
        return QTextListFormat.ListDisc

    def liste(self, el: ET.Element, ort: _Ort, listen: dict | None = None, stil: str | None = None, ebene: int = 1) -> None:
        stil = el.get(_q("text:style-name")) or stil
        listen = {} if listen is None else listen
        for punkt in el:
            if punkt.tag not in (_q("text:list-item"), _q("text:list-header")):
                continue
            for k in punkt:
                if k.tag in (_q("text:p"), _q("text:h")):
                    self.absatz(k, ort, (listen, stil or self.stile.liste_von(k.get(_q("text:style-name"))), ebene)
                                if punkt.tag == _q("text:list-item") else None)
                elif k.tag == _q("text:list"):
                    self.liste(k, ort, listen, stil, ebene + 1)
                else:
                    self.bereich([k], ort)

    # ---- Tabellen -------------------------------------------------------------------------------------------------------
    def tabelle(self, el: ET.Element, ort: _Ort) -> None:
        breiten: list[float] = []
        zeilen: list[ET.Element] = []

        def sammeln(e: ET.Element) -> None:
            for k in e:
                if k.tag == _q("table:table-column"):
                    n = min(MAX_WIEDERHOLUNG, int(k.get(_q("table:number-columns-repeated"), "1") or 1))
                    b = _px(self.stile.eigenschaften("table-column", k.get(_q("table:style-name")), "table-column")
                            .get("style:column-width"))
                    breiten.extend([b] * n)
                elif k.tag == _q("table:table-row"):
                    n = min(MAX_WIEDERHOLUNG, int(k.get(_q("table:number-rows-repeated"), "1") or 1))
                    zeilen.extend([k] * n)
                elif k.tag in (_q("table:table-columns"), _q("table:table-header-columns"), _q("table:table-rows"),
                               _q("table:table-header-rows"), _q("table:table-column-group"), _q("table:table-row-group")):
                    sammeln(k)
        sammeln(el)
        zellen = []
        for z in zeilen:
            reihe = []
            for c in z:
                if c.tag in (_q("table:table-cell"), _q("table:covered-table-cell")):
                    n = min(MAX_WIEDERHOLUNG, int(c.get(_q("table:number-columns-repeated"), "1") or 1))
                    reihe.extend([c] * n)
            zellen.append(reihe)
        spalten = max([len(r) for r in zellen] + [len(breiten), 1])
        if not zeilen:
            return
        tf = QTextTableFormat()
        tf.setCellPadding(4)
        tf.setCellSpacing(0)
        tf.setBorder(1)
        tf.setBorderBrush(QBrush(QColor("#000000")))
        tf.setBorderStyle(QTextFrameFormatBorder)
        if breiten and len(breiten) == spalten and sum(breiten) > 0:
            tf.setColumnWidthConstraints([QTextLength(QTextLength.PercentageLength, 100 * b / sum(breiten)) for b in breiten])
        if not ort.frei:
            ort.cur.insertBlock()
        t = ort.cur.insertTable(len(zeilen), spalten, tf)
        for r, reihe in enumerate(zellen):
            for c, zelle in enumerate(reihe):
                if zelle.tag != _q("table:table-cell"):
                    continue
                zelle_ort = _Ort(t.cellAt(r, c).firstCursorPosition())
                hg = self.stile.eigenschaften("table-cell", zelle.get(_q("table:style-name")), "table-cell").get("fo:background-color")
                if hg and hg != "transparent" and QColor(hg).isValid():
                    zf = t.cellAt(r, c).format()
                    zf.setBackground(QBrush(QColor(hg)))
                    t.cellAt(r, c).setFormat(zf)
                self.bereich(list(zelle), zelle_ort)
                zs = int(zelle.get(_q("table:number-rows-spanned"), "1") or 1)
                ss = int(zelle.get(_q("table:number-columns-spanned"), "1") or 1)
                if zs > 1 or ss > 1:
                    t.mergeCells(r, c, min(zs, len(zeilen) - r), min(ss, spalten - c))
        ort.cur = QTextCursor(self.doc)
        ort.cur.setPosition(t.lastPosition() + 1)
        ort.frei = True

    # ---- Ablauf ---------------------------------------------------------------------------------------------------------
    def bereich(self, kinder, ort: _Ort) -> None:
        for k in kinder:
            t = k.tag
            if t in (_q("text:p"), _q("text:h")):
                self.absatz(k, ort)
            elif t == _q("text:list"):
                self.liste(k, ort)
            elif t == _q("table:table"):
                self.tabelle(k, ort)
            elif t in (_q("text:section"), _q("text:index-body"), _q("text:table-of-content"),
                       _q("text:alphabetical-index"), _q("text:illustration-index"), _q("text:table-index"),
                       _q("text:bibliography"), _q("text:user-index"), _q("text:object-index")):
                self.bereich(list(k), ort)
            elif t == _q("draw:frame"):
                self.rahmen(k, ort.cur)
                ort.frei = False

    def seite(self) -> PageSettings:
        page = PageSettings()
        wurzel = self.stil_wurzel
        master = None
        ms = wurzel.find(_q("office:master-styles")) if wurzel is not None else None
        if ms is not None:
            alle = ms.findall(_q("style:master-page"))
            master = next((m for m in alle if m.get(_q("style:name")) == "Standard"), alle[0] if alle else None)
        if master is None:
            return page
        layout = self.stile.seiten.get(master.get(_q("style:page-layout-name"), ""))
        if layout is not None:
            p = layout.find(_q("style:page-layout-properties"))
            a = {_kurz(k): v for k, v in (p.attrib.items() if p is not None else [])}
            mm = lambda w, s: px_to_mm(_px(w, s * 96 / 25.4)) if w else s      # noqa: E731
            page.width_mm = mm(a.get("fo:page-width"), page.width_mm)
            page.height_mm = mm(a.get("fo:page-height"), page.height_mm)
            page.margin_left_mm = mm(a.get("fo:margin-left"), page.margin_left_mm)
            page.margin_right_mm = mm(a.get("fo:margin-right"), page.margin_right_mm)
            oben = mm(a.get("fo:margin-top"), page.margin_top_mm)
            unten = mm(a.get("fo:margin-bottom"), page.margin_bottom_mm)
            hg = a.get("fo:background-color")
            if hg and hg != "transparent":
                page.color = hg
            # ODF misst den Rand bis zur Kopfzeile; Lunivo (wie Word) bis zum Text: Kopfzeilenhöhe und Abstand kommen dazu.
            kopf_da = master.find(_q("style:header")) is not None or master.find(_q("style:header-first")) is not None
            fuss_da = master.find(_q("style:footer")) is not None or master.find(_q("style:footer-first")) is not None
            page.margin_top_mm, page.margin_bottom_mm = oben, unten
            for teil, da, kante in (("header", kopf_da, "bottom"), ("footer", fuss_da, "top")):
                hp = layout.find(f"{_q('style:' + teil + '-style')}/{_q('style:header-footer-properties')}")
                if not da or hp is None:
                    continue
                h = {_kurz(k): v for k, v in hp.attrib.items()}
                extra = px_to_mm(_px(h.get("fo:min-height") or h.get("svg:height"), 0) + _px(h.get(f"fo:margin-{kante}"), 0))
                if teil == "header":
                    page.kopf_abstand_mm = oben
                    page.margin_top_mm = oben + max(extra, 5.0)
                else:
                    page.fuss_abstand_mm = unten
                    page.margin_bottom_mm = unten + max(extra, 5.0)
        page.header = self._kopf_fuss(master.find(_q("style:header")))
        page.footer = self._kopf_fuss(master.find(_q("style:footer")))
        erste_kopf, erste_fuss = master.find(_q("style:header-first")), master.find(_q("style:footer-first"))
        if erste_kopf is not None or erste_fuss is not None:
            page.diff_first = True
            page.first_header = self._kopf_fuss(erste_kopf)
            page.first_footer = self._kopf_fuss(erste_fuss)
        if any(k.find(".//" + _q("draw:frame")) is not None for k in master):
            self.report.warn("Bilder in Kopf- und Fußzeile aus der ODT-Datei wurden nicht übernommen.")
        return page

    def _kopf_fuss(self, el: ET.Element | None) -> HeaderFooter:
        if el is None or el.get(_q("style:display")) == "false":
            return HeaderFooter()
        absaetze = [p for p in el.iter() if p.tag in (_q("text:p"), _q("text:h"))]
        text = "\n".join(_text_von(p) for p in absaetze).strip("\n")
        ausr = "center"
        if absaetze:
            a = self.stile.eigenschaften("paragraph", absaetze[0].get(_q("text:style-name")), "paragraph").get("fo:text-align")
            ausr = {"start": "left", "left": "left", "end": "right", "right": "right", "justify": "justify"}.get(a or "", "center")
        return HeaderFooter(text, ausr)

    def run(self):
        koerper = self.inhalt.find(f"{_q('office:body')}/{_q('office:text')}")
        if koerper is None:
            raise DocumentIOError("Die Datei ist kein OpenDocument-Text (ODT) oder beschädigt.")
        page = self.seite()
        tp = self.stile.eigenschaften("paragraph", "Standard", "text")
        df = QFont(self.stile.schriften.get(tp.get("style:font-name", ""), "") or tp.get("fo:font-family", "").strip("'\"")
                   or "Liberation Serif")
        df.setPointSizeF(_pt(tp.get("fo:font-size")) or 12.0)
        self.doc.setDefaultFont(df)
        self.bereich(list(koerper), _Ort(QTextCursor(self.doc)))
        meta = {"title": "", "author": ""}
        if self.meta_el is not None:
            titel = self.meta_el.find(f".//{_q('dc:title')}")
            autor = self.meta_el.find(f".//{_q('meta:initial-creator')}")
            if autor is None:
                autor = self.meta_el.find(f".//{_q('dc:creator')}")
            meta["title"] = (titel.text or "") if titel is not None else ""
            meta["author"] = (autor.text or "") if autor is not None else ""
        from lunivo_writer.editor.zusatz import leere_meta
        meta.update(leere_meta())
        self.doc.setModified(False)
        return self.doc, page, meta, self.report


from PySide6.QtGui import QTextFrameFormat as _QTFF                     # noqa: E402

QTextFrameFormatBorder = _QTFF.BorderStyle_Solid


def _xml(daten: bytes) -> ET.Element:
    try:
        return ET.fromstring(daten)
    except ET.ParseError as e:
        raise DocumentIOError("Die Datei ist kein gültiges OpenDocument oder beschädigt.") from e


def read_odt(path: str):
    """→ (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError."""
    try:
        z = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError) as e:
        raise DocumentIOError("Die Datei ist kein gültiges ODT-Dokument oder beschädigt.") from e
    with z:
        if sum(i.file_size for i in z.infolist()) > GRENZE_BYTES:
            raise DocumentIOError("Die ODT-Datei ist entpackt zu groß, um sie sicher zu öffnen.")
        namen = set(z.namelist())
        if "content.xml" not in namen:
            raise DocumentIOError("Die Datei ist kein gültiges ODT-Dokument oder beschädigt (content.xml fehlt).")
        try:
            inhalt = _xml(z.read("content.xml"))
            stile = _xml(z.read("styles.xml")) if "styles.xml" in namen else None
            meta = _xml(z.read("meta.xml")) if "meta.xml" in namen else None
        except (zipfile.BadZipFile, KeyError, OSError) as e:
            raise DocumentIOError("Die Datei ist kein gültiges ODT-Dokument oder beschädigt.") from e

        def bild(name: str) -> bytes | None:
            try:
                return z.read(name) if name in namen else None
            except (zipfile.BadZipFile, OSError):
                return None
        return _Leser(inhalt, stile, meta, bild).run()


def read_fodt(path: str):
    """Flaches ODT (eine XML-Datei)."""
    try:
        with open(path, "rb") as fh:
            daten = fh.read(GRENZE_BYTES + 1)
    except OSError as e:
        raise DocumentIOError(f"Datei nicht lesbar: {e.strerror or e}") from e
    if len(daten) > GRENZE_BYTES:
        raise DocumentIOError("Die Datei ist zu groß, um sie sicher zu öffnen.")
    wurzel = _xml(daten)
    return _Leser(wurzel, wurzel, wurzel.find(_q("office:meta")), lambda _n: None).run()
