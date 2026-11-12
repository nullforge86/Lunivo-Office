"""ODT und FODT (OpenDocument-Text) direkt lesen — ohne Umwandlungsprogramm.

Gelesen werden ``content.xml`` (Text), ``styles.xml`` (Vorlagen, Seite, Kopf- und Fußzeile), ``meta.xml`` (Titel, Autor) und die Bilder
aus ``Pictures/``; FODT ist dasselbe als eine einzige XML-Datei. Übernommen: Absätze und Überschriften mit Ausrichtung, Einzügen,
Abständen und Seitenumbruch; Zeichenformat (Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen, hoch/tief, Farbe,
Hintergrund); Listen; Tabellen (auch verbundene Zellen); Bilder; Seitengröße, Seitenränder, Kopf- und Fußzeile mit Seitenzahl.
Was nicht übernommen wird (Kommentare, Textrahmen und komplexe Zeichnungen), meldet der Bericht; einfache freie Rechtecke und Ellipsen laufen als native Formen.
"""
from __future__ import annotations

import zipfile
import xml.etree.ElementTree as ET

from PySide6.QtCore import Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QImage, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument,
                           QTextFormat, QTextLength, QTextListFormat, QTextTableFormat)

from lunivo_writer.modelle.seite import HeaderFooter, PageSettings, px_to_mm
from lunivo_writer.modelle.bericht import DocumentIOError, IOReport

from lunivo_writer.dienste.odt_xml import (
    NS, GRENZE_BYTES, MAX_WIEDERHOLUNG, _PX, _q, _px, _pt, _text_von, _PRAEFIX, _kurz,
)


from lunivo_writer.dienste.odt_stile import _Stile, _zeichenformat, _absatzformat


class _Ort:
    """Wohin der nächste Absatz kommt: ein Cursor und ob dessen Block noch leer und frei ist."""

    def __init__(self, cur: QTextCursor, frei: bool = True):
        self.cur, self.frei = cur, frei


# Inline-Elemente: Zeichen, Warnungen und stillschweigend Übergangenes (alles übrige — Verweise, Felder — zeigt seinen Text)
_INLINE_ZEICHEN = {_q("text:tab"): "\t", _q("text:line-break"): "\u2028"}
_INLINE_WARNUNG = {_q("office:annotation"): "Kommentare aus der ODT-Datei wurden nicht übernommen."}
_INLINE_UEBERSPRINGEN = frozenset(_q(t) for t in (
    "office:annotation-end", "text:soft-page-break", "text:bookmark", "text:bookmark-start", "text:bookmark-end",
    "text:reference-mark", "text:reference-mark-start", "text:reference-mark-end", "text:alphabetical-index-mark",
    "text:toc-mark", "text:change-start", "text:change-end", "text:change"))


def _leerzeichen_anzahl(el: ET.Element) -> int:
    """``text:s``: Anzahl der Leerzeichen (1 bis 1000, bei ungültigem Wert 1)."""
    try:
        return max(1, min(1000, int(el.get(_q("text:c"), "1"))))
    except ValueError:
        return 1


from lunivo_writer.dienste.odt_bilder import _ODTBilder
from lunivo_writer.dienste.odt_listen_lesen import _ODTListen
from lunivo_writer.dienste.odt_seite_lesen import _ODTSeite


class _Leser(_ODTBilder, _ODTSeite, _ODTListen):
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
        self.noten = {"f": {}, "e": {}}
        self._noten_zaehler = {"f": 0, "e": 0}

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
            self._inline_kind(k, cur, eltern, cf)
            if k.tail:
                cur.insertText(k.tail, cf)

    def _inline_kind(self, k: ET.Element, cur: QTextCursor, eltern: dict[str, str], cf: QTextCharFormat) -> None:
        t = k.tag
        if t == _q("text:span"):
            p = dict(eltern)
            p.update(self.stile.eigenschaften("text", k.get(_q("text:style-name")), "text"))
            self.inline(k, cur, p)
        elif t == _q("text:s"):
            cur.insertText(" " * _leerzeichen_anzahl(k), cf)
        elif t in _INLINE_ZEICHEN:
            cur.insertText(_INLINE_ZEICHEN[t], cf)
        elif t == _q("draw:frame"):
            self.rahmen(k, cur)
        elif t in (_q("draw:rect"), _q("draw:ellipse")):
            self.form(k, cur)
        elif t == _q("text:note"):
            self._note(k, cur, cf)
        elif t in _INLINE_WARNUNG:
            self.report.warn(_INLINE_WARNUNG[t])
        elif t in _INLINE_UEBERSPRINGEN:
            pass
        elif t.startswith("{" + NS["draw"]):
            self.report.warn("Zeichnungen und Formen aus der ODT-Datei wurden nicht übernommen.")
        else:                                                 # Verweise, Meta, Felder (Datum, Seitenzahl …): der angezeigte Text
            self.inline(k, cur, eltern)

    def _note(self, node: ET.Element, cur: QTextCursor, cf: QTextCharFormat) -> None:
        """ODT-Fuß-/Endnote: sichtbare Marke im Text, Inhalt in den Dokumentzusatzdaten."""
        art = "e" if node.get(_q("text:note-class")) == "endnote" else "f"
        self._noten_zaehler[art] += 1
        raw_id = node.get(_q("text:id"), "")
        suffix = raw_id.rstrip("0123456789")
        ziffern = raw_id[len(suffix):]
        nid = int(ziffern) if ziffern else self._noten_zaehler[art]
        while nid in self.noten[art]:
            nid += 1
        citation = node.find(_q("text:note-citation"))
        marke = "".join(citation.itertext()) if citation is not None else str(self._noten_zaehler[art])
        from lunivo_writer.editor.dokument.zusatz import P_NOTE
        nf = QTextCharFormat(cf)
        nf.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        nf.setProperty(P_NOTE, f"{art}:{nid}")
        cur.insertText(marke, nf)
        body = node.find(_q("text:note-body"))
        zeilen = ["".join(p.itertext()).strip() for p in body.iter(_q("text:p"))] if body is not None else []
        self.noten[art][nid] = "\n".join(zeilen)

    # ---- Tabellen -------------------------------------------------------------------------------------------------------
    def tabelle(self, el: ET.Element, ort: _Ort) -> None:
        from lunivo_writer.dienste.odt_tabellen import tabelle
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
            elif t in (_q("draw:rect"), _q("draw:ellipse")):
                self.form(k, ort.cur)
                ort.frei = False

    def _standardschrift(self) -> QFont:
        tp = self.stile.eigenschaften("paragraph", "Standard", "text")
        df = QFont(self.stile.schriften.get(tp.get("style:font-name", ""), "") or tp.get("fo:font-family", "").strip("'\"")
                   or "Liberation Serif")
        df.setPointSizeF(_pt(tp.get("fo:font-size")) or 12.0)
        return df

    def _meta(self) -> dict:
        """Titel und Autor aus ``meta.xml`` (bzw. ``office:meta``), dazu die leeren Zusatzfelder."""
        meta = {"title": "", "author": ""}
        if self.meta_el is not None:
            titel = self.meta_el.find(f".//{_q('dc:title')}")
            autor = self.meta_el.find(f".//{_q('meta:initial-creator')}")
            if autor is None:
                autor = self.meta_el.find(f".//{_q('dc:creator')}")
            meta["title"] = (titel.text or "") if titel is not None else ""
            meta["author"] = (autor.text or "") if autor is not None else ""
        from lunivo_writer.editor.dokument.zusatz import leere_meta
        meta.update(leere_meta())
        meta["noten"] = {art: dict(eintraege) for art, eintraege in self.noten.items()}
        return meta

    def run(self):
        koerper = self.inhalt.find(f"{_q('office:body')}/{_q('office:text')}")
        if koerper is None:
            raise DocumentIOError("Die Datei ist kein OpenDocument-Text (ODT) oder beschädigt.")
        page = self.seite()
        self.doc.setDefaultFont(self._standardschrift())
        self.bereich(list(koerper), _Ort(QTextCursor(self.doc)))
        meta = self._meta()
        self.doc.setModified(False)
        return self.doc, page, meta, self.report


from PySide6.QtGui import QTextFrameFormat as _QTFF                     # noqa: E402

QTextFrameFormatBorder = _QTFF.BorderStyle_Solid


def _xml(daten: bytes) -> ET.Element:
    from lunivo_writer.dienste.import_grenzen import sicheres_xml
    return sicheres_xml(daten)                       # ohne DTD/Entitäten, mit Tiefengrenze; wirft DocumentIOError


def read_odt(path: str):
    """→ (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError."""
    from lunivo_writer.dienste.import_grenzen import pruefe_paket
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
