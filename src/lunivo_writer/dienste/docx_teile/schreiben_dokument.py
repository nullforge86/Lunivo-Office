"""DOCX schreiben: Dokument – fachlich gekapselte Verarbeitung."""
from __future__ import annotations

from lunivo_writer.dienste.docx_teile.schreiben_gemeinsam import (  # noqa: F401
    io,
    logging,
    os,
    Optional,
    docx,
    WD_ORIENT,
    WD_STYLE_TYPE,
    WD_ALIGN_PARAGRAPH,
    WD_LINE_SPACING,
    RT,
    OxmlElement,
    qn,
    Emu,
    Mm,
    Pt,
    RGBColor,
    QBuffer,
    QIODevice,
    QUrl,
    Qt,
    QFont,
    QImage,
    QTextBlock,
    QTextBlockFormat,
    QTextCharFormat,
    QTextDocument,
    QTextFormat,
    QTextFrameFormat,
    QTextFrame,
    QTextListFormat,
    QTextTable,
    PageSettings,
    LH_FIXED,
    LH_PROPORTIONAL,
    STYLE_PROP,
    DocumentIOError,
    IOReport,
    Farbe,
    PX_TO_PT,
    EMU_PER_PX,
    _LIST_STYLES,
    _has,
    abstand_davor_px,
    B_BILDANKER,
    B_SPALTE,
    P_OBJEKT,
    P_VERSTECKT,
    P_FORM,
    B_ABSCHNITT,
    umbruch,
    Linie,
    art_aus_docx,
    docx_wert,
    muster,
    B_ART,
    B_CAP,
    B_MUSTER,
    B_RAHMEN,
    B_TOC,
    P_AENDERUNG,
    P_AUTOR,
    P_DATUM,
    P_FELD,
    P_INDEX,
    P_KOMMENTAR,
    P_NOTE,
    _RPR_FOLGE,
    _rpr_einfuegen,
    absatzopt_prop,
    _split,
    _rstyle_hyperlink,
    _Body,
    _CellBox,
)

class SchreibenDokumentMixin:
    """Fachliche Teilverantwortung des DOCX-Writers."""

    def _clear_body(self):
        body = self.d.element.body
        for el in list(body):
            if el.tag != qn("w:sectPr"):
                body.remove(el)

    def _standard_tabstopp(self) -> None:
        """Die Standardtabstopps des Dokuments als w:defaultTabStop (Twips) in die Einstellungen schreiben."""
        from lunivo_writer.modelle.seite import px_to_mm
        dist = self.q.defaultTextOption().tabStopDistance()
        st = self.d.settings.element
        for alt in st.findall(qn("w:defaultTabStop")):
            st.remove(alt)
        if dist <= 0:
            return
        e = OxmlElement("w:defaultTabStop"); e.set(qn("w:val"), str(int(round(px_to_mm(dist) / 25.4 * 1440))))
        nach = ("w:autoHyphenation", "w:consecutiveHyphenLimit", "w:hyphenationZone", "w:doNotHyphenateCaps", "w:showEnvelope", "w:summaryLength",
                "w:clickAndTypeStyle", "w:defaultTableStyle", "w:evenAndOddHeaders", "w:bookFoldRevPrinting", "w:bookFoldPrinting", "w:bookFoldPrintingSheets",
                "w:drawingGridHorizontalSpacing", "w:drawingGridVerticalSpacing", "w:displayHorizontalDrawingGridEvery", "w:displayVerticalDrawingGridEvery",
                "w:doNotUseMarginsForDrawingGridOrigin", "w:drawingGridHorizontalOrigin", "w:drawingGridVerticalOrigin", "w:doNotShadeFormData",
                "w:noPunctuationKerning", "w:characterSpacingControl", "w:printTwoOnOne", "w:strictFirstAndLastChars", "w:noLineBreaksAfter",
                "w:noLineBreaksBefore", "w:savePreviewPicture", "w:doNotValidateAgainstSchema", "w:saveInvalidXml", "w:ignoreMixedContent",
                "w:alwaysShowPlaceholderText", "w:doNotDemarcateInvalidXml", "w:saveXmlDataOnly", "w:useXSLTWhenSaving", "w:saveThroughXslt",
                "w:showXMLTags", "w:alwaysMergeEmptyNamespace", "w:updateFields", "w:hdrShapeDefaults", "w:footnotePr", "w:endnotePr", "w:compat",
                "w:docVars", "w:rsids", "w:mathPr", "w:attachedSchema", "w:themeFontLang", "w:clrSchemeMapping", "w:doNotIncludeSubdocsInStats",
                "w:doNotAutoCompressPictures", "w:forceUpgrade", "w:captions", "w:readModeInkLockDown", "w:smartTagType", "w:schemaLibrary",
                "w:shapeDefaults", "w:doNotEmbedSmartTags", "w:decimalSymbol", "w:listSeparator")
        st.insert_element_before(e, *nach)

    def _dokument_ebene(self, p) -> None:
        self._standard_tabstopp()
        doc_el = self.d.element
        for alt in doc_el.findall(qn("w:background")):
            doc_el.remove(alt)
        if p.color:
            bg = OxmlElement("w:background")
            bg.set(qn("w:color"), p.color.lstrip("#").upper())
            doc_el.insert(0, bg)
            st = self.d.settings.element
            if st.find(qn("w:displayBackgroundShape")) is None:
                st.insert(0, OxmlElement("w:displayBackgroundShape"))
        st = self.d.settings.element
        for alt in st.findall(qn("w:autoHyphenation")):
            st.remove(alt)
        if p.silbentrennung:
            ah = OxmlElement("w:autoHyphenation")
            anker = st.find(qn("w:zoom"))
            (anker.addnext(ah) if anker is not None else st.insert(0, ah))

    def _text_with_fields(self, para, text: str):
        import re
        for tok in re.split(r"(\{PAGE\}|\{PAGES\})", text):
            if tok in ("{PAGE}", "{PAGES}"):
                self._field(para, "PAGE" if tok == "{PAGE}" else "NUMPAGES")
            elif tok:
                para.add_run(tok)

    @staticmethod
    def _field(para, name: str):
        run = para.add_run()
        for kind, extra in (("begin", None), (None, f" {name} "), ("separate", None), (None, "1"), ("end", None)):
            if kind:
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), kind)
                run._r.append(el)
            elif extra.strip() == name:
                it = OxmlElement("w:instrText")
                it.set(qn("xml:space"), "preserve")
                it.text = extra
                run._r.append(it)
            else:
                t = OxmlElement("w:t")
                t.text = extra
                run._r.append(t)

    # ---- Grundschrift --------------------------------------------------

    def _sprache(self) -> None:
        # Ohne Angabe gilt die Sprache des Dokuments (Silbentrennung/Korrektur), nicht die Vorgabe „en-US“ der Vorlage —
        # sonst prüfen andere Programme deutschen Text als Englisch und unterringeln jedes Wort.
        kennung = self.meta.get("sprache") or str(getattr(self.page, "silben_sprache", "") or "").replace("_", "-")
        if not kennung:
            return
        rpr = self.d.styles.element.find(qn("w:docDefaults") + "/" + qn("w:rPrDefault") + "/" + qn("w:rPr"))
        if rpr is None:
            return
        lang = rpr.find(qn("w:lang"))
        if lang is None:
            lang = OxmlElement("w:lang")
            rpr.append(lang)
        lang.set(qn("w:val"), kennung)

    def write_defaults(self):
        f: QFont = self.q.defaultFont()
        normal = self.d.styles["Normal"]
        normal.font.name = f.family()
        if f.pointSizeF() > 0:
            normal.font.size = Pt(f.pointSizeF())
        rpr = normal.element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.insert(0, rf)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(a), f.family())
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
            if rf.get(qn(a)) is not None:
                del rf.attrib[qn(a)]
        pf = normal.paragraph_format
        pf.space_after = Pt(0)
        pf.space_before = Pt(0)

    # ---- Durchlauf -----------------------------------------------------
