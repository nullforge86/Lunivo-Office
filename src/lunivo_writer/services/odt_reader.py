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

from lunivo_writer.services.odt_xml import (
    NS, GRENZE_BYTES, MAX_WIEDERHOLUNG, _PX, _q, _px, _pt, _text_von, _PRAEFIX, _kurz,
)


from lunivo_writer.services.odt_stile import _Stile, _zeichenformat, _absatzformat
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

    def _bild_laden(self, bild: ET.Element) -> QImage:
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
        return img

    def _frei_angabe(self, frame: ET.Element) -> dict | None:
        """Ein Rahmen am Absatz oder an der Seite, den kein Text umfließt → Angabe wie in editor/freie_bilder.py, sonst None."""
        from lunivo_writer.services.odt_writer import AUSR_H, AUSR_V, BEZUG_H, BEZUG_V
        anker = frame.get(_q("text:anchor-type"), "as-char")
        if anker not in ("paragraph", "char", "page"):
            return None
        g = self.stile.eigenschaften("graphic", frame.get(_q("draw:style-name")), "graphic")
        if g.get("style:wrap") != "run-through":                # umflossene Bilder bleiben Bilder im Text
            return None
        zurueck = lambda tab, wert, standard: next((k for k, v in tab.items() if v == wert), standard)   # noqa: E731
        hpos, vpos = g.get("style:horizontal-pos", "from-left"), g.get("style:vertical-pos", "from-top")
        return {"b": _px(frame.get(_q("svg:width")), 0.0) or None, "h": _px(frame.get(_q("svg:height")), 0.0) or None,
                "hinter": g.get("style:run-through") == "background",
                "bh": "seite" if anker == "page" else zurueck(BEZUG_H, g.get("style:horizontal-rel", "paragraph"), "spalte"),
                "bv": "seite" if anker == "page" else zurueck(BEZUG_V, g.get("style:vertical-rel", "paragraph"), "absatz"),
                "ah": zurueck(AUSR_H, hpos, ""), "av": zurueck(AUSR_V, vpos, ""),
                "xh": _px(frame.get(_q("svg:x")), 0.0), "yv": _px(frame.get(_q("svg:y")), 0.0), "ellipse": False}

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
        img = self._bild_laden(bild)
        if img.isNull():
            self.report.warn("Ein Bild aus der ODT-Datei war nicht lesbar und wurde übersprungen.")
            return
        angabe = self._frei_angabe(frame)
        if angabe is not None:                                 # frei auf dem Blatt (am Absatz): als Bildanker des Absatzes
            from lunivo_writer.editor import freie_bilder as FB
            name = FB.neuer_name(self.doc)
            self.doc.addResource(QTextDocument.ImageResource, QUrl(name), img)
            angabe.update(n=name, b=angabe["b"] or img.width(), h=angabe["h"] or img.height())
            FB.an_absatz(cur, angabe)
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
        from lunivo_writer.services.odt_tabellen import tabelle
        tabelle(self, el, ort)

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
            page.seiten_format = {"a": "klein", "A": "gross", "i": "roem_klein", "I": "roem_gross"}.get(a.get("style:num-format", "1"), "dezimal")
            oben = mm(a.get("fo:margin-top"), page.margin_top_mm)
            unten = mm(a.get("fo:margin-bottom"), page.margin_bottom_mm)
            hg = a.get("fo:background-color")
            if hg and hg != "transparent":
                page.color = hg
            # ODF misst den Rand bis zur Kopfzeile; Lunivo bis zum Text: Kopfzeilenhöhe und Abstand kommen dazu.
            kopf_da = master.find(_q("style:header")) is not None or master.find(_q("style:header-first")) is not None \
                or master.find(_q("style:header-left")) is not None
            fuss_da = master.find(_q("style:footer")) is not None or master.find(_q("style:footer-first")) is not None \
                or master.find(_q("style:footer-left")) is not None
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
        for attr, tag in (("header", "header-left"), ("footer", "footer-left")):          # gespiegelt auf linken Seiten: „außen“/„innen“
            hf, links = getattr(page, attr), self._kopf_fuss(master.find(_q("style:" + tag)))
            if hf.text and links.text == hf.text and {hf.align, links.align} == {"left", "right"}:
                hf.align = "aussen" if hf.align == "right" else "innen"
            elif links.text and (links.text != hf.text or links.align != hf.align):
                page.diff_even = True                                  # eigene Zeilen für gerade Seiten
                setattr(page, "even_" + attr, links)
        erste_kopf, erste_fuss = master.find(_q("style:header-first")), master.find(_q("style:footer-first"))
        if erste_kopf is not None or erste_fuss is not None:
            page.diff_first = True
            page.first_header = self._kopf_fuss(erste_kopf)
            page.first_footer = self._kopf_fuss(erste_fuss)
        for tag, ort in (("header", "kopf"), ("footer", "fuss"), ("header-first", "kopf1"), ("footer-first", "fuss1")):
            teil = master.find(_q("style:" + tag))
            if teil is None:
                continue
            for fr in teil.iter(_q("draw:frame")):
                bild = fr.find(_q("draw:image"))
                img = self._bild_laden(bild) if bild is not None else QImage()
                angabe = self._frei_angabe(fr) if not img.isNull() else None
                if angabe is None:
                    self.report.warn("Ein Bild in der Kopf- oder Fußzeile der ODT-Datei wurde nicht übernommen.")
                    continue
                angabe.update(ort=ort, bild=img, b=angabe["b"] or img.width(), h=angabe["h"] or img.height())
                page.bilder.append(angabe)
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
    from lunivo_writer.services.import_grenzen import sicheres_xml
    return sicheres_xml(daten)                       # ohne DTD/Entitäten, mit Tiefengrenze; wirft DocumentIOError


def read_odt(path: str):
    """→ (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError."""
    from lunivo_writer.services.import_grenzen import pruefe_paket
    pruefe_paket(path, "ODT")                        # Grenzen zuerst, bevor irgendetwas gelesen wird
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
