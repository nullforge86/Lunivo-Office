"""DOCX lesen: Metadaten – fachlich gekapselte Verarbeitung."""
from __future__ import annotations

from lunivo_writer.services.docx_teile.lesen_gemeinsam import (  # noqa: F401
    io,
    logging,
    zipfile,
    Optional,
    docx,
    _Document,
    WD_STYLE_TYPE,
    WD_ALIGN_PARAGRAPH,
    qn,
    Table,
    Hyperlink,
    Run,
    Paragraph,
    QUrl,
    QBrush,
    QColor,
    QFont,
    QImage,
    QTextBlockFormat,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextFormat,
    QTextFrameFormat,
    QTextImageFormat,
    QTextLength,
    QTextListFormat,
    QTextTableFormat,
    HeaderFooter,
    PageSettings,
    mm_to_px,
    px_to_mm,
    DocumentIOError,
    IOReport,
    LH_PROPORTIONAL,
    LH_FIXED,
    Farbe,
    STYLE_PROP,
    B_SPALTE,
    P_OBJEKT,
    P_VERSTECKT,
    P_FORM,
    Linie,
    art_aus_docx,
    docx_wert,
    muster,
    B_ART,
    B_CAP,
    B_MUSTER,
    B_RAHMEN,
    B_TOC,
    BESCHRIFTUNGEN,
    P_AENDERUNG,
    P_AUTOR,
    P_DATUM,
    P_FELD,
    P_INDEX,
    P_KOMMENTAR,
    P_NOTE,
    P_ZITAT,
    leere_meta,
    EMU_PER_PX,
    PT_PER_PX,
    HEADING_DEFAULT_PT,
    NAMED_STYLE_DEFAULT,
    Qt,
    _QT_ALIGN,
    _MC_ALT,
    _MC_CHOICE,
    _UNSUPPORTED,
    _NS_DOCX,
    _WPS,
    _NS,
    _xp,
    _emu_to_px,
    _pt_to_px,
    lxml_parser,
    _style_chain,
    _doc_defaults,
    _NoRun,
    _ERSATZ,
)

class LesenMetadatenMixin:
    """Fachliche Teilverantwortung des DOCX-Readers."""

    def _laden_zusatz(self) -> None:
        """Kommentare (python-docx) und Fuß-/Endnoten (Teile footnotes.xml / endnotes.xml) einlesen."""
        self._kommentare_lesen()
        self._kommentare_geloest_lesen()
        self._quellen_lesen()
        for art, rel in (("f", "footnotes"), ("e", "endnotes")):
            for r in self.d.part.rels.values():
                if r.reltype.endswith("/" + rel) and not r.is_external:
                    self._noten_lesen(art, r.target_part.blob)

    def _kommentare_lesen(self) -> None:
        try:
            for c in self.d.comments:
                self.zus["kommentare"][int(c.comment_id)] = {
                    "autor": c.author or "", "initialen": c.initials or "",
                    "datum": c.timestamp.isoformat() if c.timestamp else "",
                    "text": "\n".join(p.text for p in c.paragraphs)}
        except Exception:
            self.report.warn("Kommentare konnten nicht gelesen werden.")

    def _noten_lesen(self, art: str, blob: bytes) -> None:
        """Noten einer Art („f“ Fußnoten, „e“ Endnoten) aus dem Teil in ``zus["noten"]`` ablegen; Trenner und Hinweise entfallen."""
        from lxml import etree
        wurzel = etree.fromstring(blob, lxml_parser())
        tag = qn("w:footnote") if art == "f" else qn("w:endnote")
        for n in wurzel.iterchildren(tag):
            if n.get(qn("w:type")) in ("separator", "continuationSeparator", "continuationNotice"):
                continue
            zeilen = ["".join(t.text or "" for t in p.iter(qn("w:t"))).strip() for p in n.iterchildren(qn("w:p"))]
            self.zus["noten"][art][int(n.get(qn("w:id")))] = "\n".join(zeilen)

    def _kommentare_geloest_lesen(self) -> None:
        """Welche Kommentare Word als gelöst markiert hat (Teil commentsExtended: w15:done je Absatzkennung)."""
        try:
            W14 = "{http://schemas.microsoft.com/office/word/2010/wordml}paraId"
            fertig = self._geloeste_kennungen()
            if not fertig:
                return
            for c in self.d.comments:
                ps = c.paragraphs
                if ps and ps[0]._p.get(W14) in fertig and int(c.comment_id) in self.zus["kommentare"]:
                    self.zus["kommentare"][int(c.comment_id)]["geloest"] = True
        except Exception:                                              # noqa: BLE001 — ein unlesbarer Zusatzteil darf das Laden nicht verhindern
            pass

    def _geloeste_kennungen(self) -> set:
        """Absatzkennungen (w15:paraId) der Kommentare, die in commentsExtended als erledigt (done) stehen."""
        from lxml import etree
        W15 = "{http://schemas.microsoft.com/office/word/2012/wordml}"
        fertig = set()
        for r in self.d.part.rels.values():
            if r.reltype.endswith("/commentsExtended") and not r.is_external:
                for e in etree.fromstring(r.target_part.blob, lxml_parser()).iter(W15 + "commentEx"):
                    if e.get(W15 + "done") in ("1", "true"):
                        fertig.add(e.get(W15 + "paraId"))
        return fertig

    def _quellen_lesen(self) -> None:
        """Literaturquellen aus dem Word-Bibliografieteil (customXml, Namensraum …/bibliography)."""
        from lxml import etree
        B = "{http://schemas.openxmlformats.org/officeDocument/2006/bibliography}"
        for r in self.d.part.rels.values():
            if r.is_external or not r.reltype.endswith("/customXml"):
                continue
            try:
                w = etree.fromstring(r.target_part.blob, lxml_parser())
            except Exception:
                continue
            if w.tag != B + "Sources":
                continue
            self.zus["zitierweise"] = (w.get("StyleName") or "APA")
            for q in w.iterchildren(B + "Source"):
                self.zus["quellen"].append(self._quelle_lesen(q, B))

    @staticmethod
    def _quelle_lesen(q, B: str) -> dict:
        """Eine Quelle (b:Source) → Angaben des Programms (Tag, Art, Autoren, Titel, Jahr, Verlag, Ort, URL)."""
        def t(n):
            e = q.find(B + n)
            return (e.text or "") if e is not None else ""
        personen = []
        for pe in q.iter(B + "Person"):
            last = (pe.findtext(B + "Last") or "").strip(); first = (pe.findtext(B + "First") or "").strip()
            personen.append(f"{last}, {first}" if first else last)
        corp = q.find(f"{B}Author/{B}Author/{B}Corporate")
        if corp is not None and corp.text:
            personen.append(corp.text)
        typ = {"Book": "Buch", "JournalArticle": "Aufsatz", "InternetSite": "Webseite", "Report": "Bericht"}.get(t("SourceType"), "Sonstiges")
        return {"tag": t("Tag"), "typ": typ, "autor": "; ".join(personen), "titel": t("Title"),
                "jahr": t("Year"), "verlag": t("Publisher"), "ort": t("City"), "url": t("URL")}

    _HL = {"yellow": "#FFFF00", "green": "#00FF00", "cyan": "#00FFFF", "magenta": "#FF00FF",
           "blue": "#0000FF", "red": "#FF0000", "darkBlue": "#000080", "darkCyan": "#008080",
           "darkGreen": "#008000", "darkMagenta": "#800080", "darkRed": "#800000",
           "darkYellow": "#808000", "darkGray": "#808080", "lightGray": "#C0C0C0",
           "black": Farbe.SCHWARZ}


    # ---- Absatzformat ------------------------------------------------
    _JC = {"left": Qt.AlignLeft, "start": Qt.AlignLeft, "right": Qt.AlignRight, "end": Qt.AlignRight, "center": Qt.AlignHCenter,
           "both": Qt.AlignJustify, "distribute": Qt.AlignJustify, "justify": Qt.AlignJustify}
