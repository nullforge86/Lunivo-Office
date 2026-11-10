"""DOCX schreiben: Absatz – fachlich gekapselte Verarbeitung."""
from __future__ import annotations

from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from PySide6.QtGui import QTextOption

from lunivo_writer.services.docx_teile.schreiben_gemeinsam import (  # noqa: F401
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

# Ausrichtung Qt → Word (erste passende gewinnt); Tabstopp-Art und Füllzeichen
_AUSRICHTUNG = ((Qt.AlignHCenter, WD_ALIGN_PARAGRAPH.CENTER), (Qt.AlignRight, WD_ALIGN_PARAGRAPH.RIGHT), (Qt.AlignJustify, WD_ALIGN_PARAGRAPH.JUSTIFY))
_TAB_ART = {QTextOption.RightTab: WD_TAB_ALIGNMENT.RIGHT, QTextOption.CenterTab: WD_TAB_ALIGNMENT.CENTER, QTextOption.DelimiterTab: WD_TAB_ALIGNMENT.DECIMAL}
_TAB_FUELLUNG = {"punkt": WD_TAB_LEADER.DOTS, "strich": WD_TAB_LEADER.DASHES, "linie": WD_TAB_LEADER.LINES, "mitte": WD_TAB_LEADER.MIDDLE_DOT}
_STIL_AUSRICHTUNG = {"links": WD_ALIGN_PARAGRAPH.LEFT, "mitte": WD_ALIGN_PARAGRAPH.CENTER,
                     "rechts": WD_ALIGN_PARAGRAPH.RIGHT, "block": WD_ALIGN_PARAGRAPH.JUSTIFY}
# Rahmenseiten (Word-Name, Kürzel) und Index der Polsterung je Kürzel (oben, unten, links, rechts)
_RAHMEN_SEITEN = (("top", "t"), ("left", "l"), ("bottom", "b"), ("right", "r"), ("between", "h"))
_POLSTER_INDEX = {"t": 0, "b": 1, "l": 2, "r": 3, "h": 0}
# Reihenfolge der Kindelemente von w:pPr (ECMA-376): Elemente, vor denen bidi bzw. shd/pBdr einzufügen sind
_PPR_NACH_BIDI = ("w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap",
                  "w:jc", "w:textDirection", "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr",
                  "w:sectPr", "w:pPrChange")
_PPR_NACH_SHD = ("w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE",
                 "w:autoSpaceDN", "w:bidi") + _PPR_NACH_BIDI


class SchreibenAbsatzMixin:
    """Fachliche Teilverantwortung des DOCX-Writers."""

    def write_frame(self, frame: QTextFrame, container):
        it = frame.begin()
        first_in_cell = isinstance(container, _CellBox)
        while not it.atEnd():
            blk = it.currentBlock()
            if blk.isValid() and umbruch.ist_anker(blk):
                it += 1                                          # Hilfsabsatz vor einem schwebenden Bild: kein Word-Absatz
                continue
            if blk.isValid():
                para = container.first_paragraph() if first_in_cell else container.add_paragraph()
                first_in_cell = False
                self.write_block(blk, para)
                if isinstance(container, _Body) and blk.blockFormat().hasProperty(B_ABSCHNITT):
                    self._abschnitt_ende(para)
            elif self._unterrahmen_schreiben(it.currentFrame(), container):
                first_in_cell = False
            it += 1

    def _unterrahmen_schreiben(self, fr, container) -> bool:
        """Tabelle, schwebendes Bild im Rahmen oder sonstiger Rahmen (als Fließtext). → True, wenn eine Tabelle geschrieben wurde."""
        if isinstance(fr, QTextTable):
            self.write_table(fr, container)
            return True
        if fr is not None and fr.frameFormat().position() in umbruch.SEITEN and umbruch.bild_im_rahmen(fr) is not None:
            self._vorab_bilder.append((umbruch.bild_im_rahmen(fr), umbruch.SEITEN[fr.frameFormat().position()]))
        elif fr is not None:
            self.report.warn("Ein Rahmen im Text wurde nur als Fließtext gespeichert.")
            self.write_frame(fr, container)
        return False

    def _eigener_stil(self, name: str):
        """Selbst angelegte Formatvorlage als echte Word-Absatzvorlage (Schrift, Größe, Farbe, Abstände, Ausrichtung)."""
        from lunivo_writer.editor.text import stile
        if not stile.ist_eigen(name):
            return None
        if name in [x.name for x in self.d.styles]:
            return self.d.styles[name]
        d = stile.definition(name)
        st = self.d.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = self.d.styles["Normal"]
        self._eigener_stil_schrift(st, d)
        self._eigener_stil_absatz(st, d)
        return st

    @staticmethod
    def _eigener_stil_schrift(st, d: dict) -> None:
        if d["groesse"]:
            st.font.size = Pt(d["groesse"])
        if d["fett"]:
            st.font.bold = True
        if d["kursiv"]:
            st.font.italic = True
        if d["schrift"]:
            st.font.name = d["schrift"]
        if d["farbe"]:
            st.font.color.rgb = RGBColor.from_string(d["farbe"].lstrip("#").upper())

    @staticmethod
    def _eigener_stil_absatz(st, d: dict) -> None:
        pf = st.paragraph_format
        pf.space_before, pf.space_after = Pt(d["vor"]), Pt(d["nach"])
        if d.get("zeilen"):
            pf.line_spacing = float(d["zeilen"])
        if d.get("einzug"):
            pf.left_indent = Mm(float(d["einzug"]))
        if d["ausr"]:
            pf.alignment = _STIL_AUSRICHTUNG[d["ausr"]]

    def write_block(self, blk: QTextBlock, para):
        bf = blk.blockFormat()
        self._freie_bilder_des_absatzes(bf, para)
        style_name = bf.property(STYLE_PROP) if _has(bf, STYLE_PROP) else None
        lvl = bf.headingLevel()
        lst = blk.textList()
        self._absatz_vorlage(bf, para, style_name, lvl, lst)
        self._absatz_einzuege(bf, para, lst)
        self._absatz_abstaende(bf, para)
        self._absatz_umbruch(bf, para)
        self._absatz_tabs(bf, para.paragraph_format)
        from lunivo_writer.editor.seite import absatzopt
        if bf.hasProperty(absatzopt_prop()):
            absatzopt.in_ppr(para._p.get_or_add_pPr(), absatzopt.lesen(bf))
        self._absatz_rahmen(bf, para)
        self._absatz_schattierung(bf, para)
        for imf, seite in self._vorab_bilder:                    # schwebende Bilder vor diesem Absatz: hier verankern
            self._image(imf, para, seite)
        self._vorab_bilder = []
        self._absatz_laufe(blk, para, bool(lvl) or style_name in ("Title", "Subtitle"))
        self._textmarken(para, [])

    def _freie_bilder_des_absatzes(self, bf: QTextBlockFormat, para) -> None:
        """Frei positionierte Bilder dieses Absatzes."""
        if bf.hasProperty(B_BILDANKER):
            from lunivo_writer.editor.objekte import freie_bilder as FB
            for a in FB.aus_absatz(bf):
                self._frei_bild(para, a, FB.bild_im_dokument(self.q, a.get("n", "")))

    @staticmethod
    def _toc_stilname(bf: QTextBlockFormat) -> str:
        """Word-Formatvorlage eines Verzeichnisabsatzes (Inhalt, Abbildungen, Index, Literatur)."""
        kind = bf.property(B_TOC)
        art = bf.property(B_ART) if bf.hasProperty(B_ART) else "toc"
        if kind == "kopf":
            return "TOC Heading"
        return {"toc": f"TOC {kind[-1]}", "abb": "Table of Figures", "tab": "Table of Figures",
                "index": f"Index {kind[-1]}", "lit": "Bibliography"}.get(art, "TOC 1")

    def _absatz_vorlage(self, bf: QTextBlockFormat, para, style_name, lvl: int, lst) -> None:
        """Formatvorlage des Absatzes: verzeichnis, Beschriftung, Überschrift, Standardvorlage, Liste, eigene Vorlage."""
        if bf.hasProperty(B_TOC):
            para.style = self._stil(self._toc_stilname(bf))
        elif bf.hasProperty(B_CAP):
            para.style = self.d.styles["Caption"]
        elif lvl:
            para.style = self.d.styles[f"Heading {lvl}"]
        elif style_name in ("Title", "Subtitle", "Quote", "No Spacing"):
            para.style = self.d.styles[style_name]
        elif lst is not None:
            self._apply_list(para, lst)
        elif style_name and str(style_name).startswith("x:") and self._eigener_stil(str(style_name)[2:]) is not None:
            para.style = self._eigener_stil(str(style_name)[2:])

    @staticmethod
    def _absatz_einzuege(bf: QTextBlockFormat, para, lst) -> None:
        """Ausrichtung, Einzüge (bei Listen steckt der Listeneinzug in der Vorlage) und Schreibrichtung."""
        pf = para.paragraph_format
        a = bf.alignment()
        for qt_ausr, wd_ausr in _AUSRICHTUNG:
            if a & qt_ausr:
                para.alignment = wd_ausr
                break
        if lst is None:
            if bf.leftMargin():
                pf.left_indent = Emu(int(bf.leftMargin() * EMU_PER_PX))
            if bf.textIndent():
                pf.first_line_indent = Emu(int(bf.textIndent() * EMU_PER_PX))
        if bf.rightMargin():
            pf.right_indent = Emu(int(bf.rightMargin() * EMU_PER_PX))
        if bf.layoutDirection() == Qt.RightToLeft:
            bidi = OxmlElement("w:bidi")
            para._p.get_or_add_pPr().insert_element_before(bidi, *_PPR_NACH_BIDI)

    @staticmethod
    def _absatz_abstaende(bf: QTextBlockFormat, para) -> None:
        """Abstand davor/danach und Zeilenabstand."""
        pf = para.paragraph_format
        pf.space_before = Pt(abstand_davor_px(bf) * PX_TO_PT)
        pf.space_after = Pt(bf.bottomMargin() * PX_TO_PT)
        lh, lht = bf.lineHeight(), bf.lineHeightType()
        if int(lht) == LH_PROPORTIONAL and lh and lh != 100:
            pf.line_spacing = lh / 100.0
        elif int(lht) == LH_FIXED and lh:
            pf.line_spacing = Pt(lh * PX_TO_PT)

    @staticmethod
    def _absatz_umbruch(bf: QTextBlockFormat, para) -> None:
        """Manueller Seiten- oder Spaltenumbruch vor dem Absatz."""
        from lunivo_writer.editor.seite.seitenfluss import ist_manuell
        if not ist_manuell(bf):
            return
        if bf.hasProperty(B_SPALTE):                              # Spaltenumbruch: <w:br w:type="column"/> am Absatzanfang
            from docx.enum.text import WD_BREAK
            para.add_run().add_break(WD_BREAK.COLUMN)
        else:
            para.paragraph_format.page_break_before = True

    @staticmethod
    def _absatz_tabs(bf: QTextBlockFormat, pf) -> None:
        """Tabstopps mit Art und Füllzeichen."""
        tabs = bf.tabPositions()
        if not tabs:
            return
        from lunivo_writer.editor.text import tabfuell
        fuell = tabfuell.lesen(bf)
        for t in tabs:
            f = next((fz for p_, fz in fuell.items() if abs(p_ - t.position) < 0.05), "")
            pf.tab_stops.add_tab_stop(Emu(int(t.position * EMU_PER_PX)), _TAB_ART.get(t.type, WD_TAB_ALIGNMENT.LEFT),
                                      _TAB_FUELLUNG.get(f, WD_TAB_LEADER.SPACES))

    @staticmethod
    def _absatz_rahmen(bf: QTextBlockFormat, para) -> None:
        """Absatzrahmen (w:pBdr) aus der Linie des Absatzes."""
        if not bf.hasProperty(B_RAHMEN):
            return
        li = Linie.aus_text(bf.stringProperty(B_RAHMEN))
        bdr = OxmlElement("w:pBdr")
        val = docx_wert(li.art)
        for seite, kurz in _RAHMEN_SEITEN:
            if kurz not in li.seiten:
                continue
            e = OxmlElement(f"w:{seite}")
            e.set(qn("w:val"), val)
            e.set(qn("w:sz"), str(max(2, int(round(li.breite_pt * 8)))))
            pol = li.polster()
            e.set(qn("w:space"), str(int(round(pol[_POLSTER_INDEX[kurz]]))) if pol else "4")
            e.set(qn("w:color"), (li.farbe or Farbe.SCHWARZ).lstrip("#").upper())
            bdr.append(e)
        if len(bdr):
            para._p.get_or_add_pPr().insert_element_before(bdr, "w:shd", *_PPR_NACH_SHD)

    @staticmethod
    def _absatz_schattierung(bf: QTextBlockFormat, para) -> None:
        """Hintergrund des Absatzes: Muster (Musterart + Farben) oder einfache Füllfarbe als w:shd."""
        bg = bf.background()
        mu = muster.aus_text(bf.stringProperty(B_MUSTER)) if bf.hasProperty(B_MUSTER) else None
        if mu:                                                   # Muster über Füllfarbe: w:val = Musterart, w:color = Musterfarbe
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), muster.ooxml_von(mu[0])); shd.set(qn("w:color"), mu[1][1:].upper()); shd.set(qn("w:fill"), mu[2][1:].upper() if mu[2] else "auto")
        elif bg.style() != Qt.NoBrush and bg.color().isValid():
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), bg.color().name()[1:].upper())
        else:
            return
        para._p.get_or_add_pPr().insert_element_before(shd, *_PPR_NACH_SHD)

    def _absatz_laufe(self, blk: QTextBlock, para, in_head: bool) -> None:
        """Fragmente des Absatzes schreiben; zusammengehörige Formularfelder und Felder werden gebündelt."""
        frags = []
        it = blk.begin()
        while not it.atEnd():
            if it.fragment().isValid():
                frags.append(it.fragment())
            it += 1
        i = 0
        while i < len(frags):
            cf = frags[i].charFormat()
            form = cf.stringProperty(P_FORM) if cf.hasProperty(P_FORM) else ""
            instr = cf.stringProperty(P_FELD) if cf.hasProperty(P_FELD) else ""
            if form:                                                   # Formularfeld → Inhaltssteuerelement (w:sdt)
                j = self._gruppe_ende(frags, i, P_FORM, form)
                self._formularfeld_schreiben(para, form, frags[i:j], in_head)
            elif instr:
                j = self._gruppe_ende(frags, i, P_FELD, instr)
                self._feld_schreiben(para, instr, frags[i:j], in_head)
            else:
                self.write_fragment(frags[i], para, in_head)
                j = i + 1
            i = j

    @staticmethod
    def _gruppe_ende(frags: list, i: int, prop: int, wert: str) -> int:
        """Index hinter dem letzten aufeinanderfolgenden Fragment mit demselben Wert der Eigenschaft."""
        j = i
        while j < len(frags) and frags[j].charFormat().hasProperty(prop) and frags[j].charFormat().stringProperty(prop) == wert:
            j += 1
        return j

    def _formularfeld_schreiben(self, para, form: str, gruppe: list, in_head: bool) -> None:
        sdt, inhalt = self._steuerelement(form, "".join(f.text() for f in gruppe))
        para._p.append(sdt)
        self._ziel = inhalt
        try:
            for frag in gruppe:
                self.write_fragment(frag, para, in_head)
        finally:
            self._ziel = None

    def _feld_schreiben(self, para, instr: str, gruppe: list, in_head: bool) -> None:
        self._textmarken(para, [])
        self._fldchar(para, "begin"); self._instr(para, instr); self._fldchar(para, "separate")
        for frag in gruppe:
            self.write_fragment(frag, para, in_head)
        self._fldchar(para, "end")

    def _stil(self, name: str):
        from docx.enum.style import WD_STYLE_TYPE
        if name not in [s.name for s in self.d.styles]:
            st = self.d.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
            st.base_style = self.d.styles["Normal"]
        return self.d.styles[name]

    @staticmethod
    def _fldchar(para, typ: str):
        r = OxmlElement("w:r")
        fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), typ)
        r.append(fc)
        para._p.append(r)

    @staticmethod
    def _instr(para, text: str):
        r = OxmlElement("w:r")
        it = OxmlElement("w:instrText"); it.set("{http://www.w3.org/XML/1998/namespace}space", "preserve"); it.text = f" {text} "
        r.append(it)
        para._p.append(r)

    def _apply_list(self, para, lst):
        fmt = lst.format()
        kind = _LIST_STYLES.get(fmt.style(), "bullet")
        level = max(1, fmt.indent())
        base = "List Bullet" if kind == "bullet" else "List Number"
        name = base if level == 1 else f"{base} {min(level, 3)}"
        try:
            para.style = self.d.styles[name]
        except KeyError:
            para.style = self.d.styles[base]
        if kind == "number":
            key = lst.item(0).blockNumber()
            if key not in self._num_ids:
                self._num_ids[key] = self._new_num_instance(para)
            numpr = para._p.get_or_add_pPr().get_or_add_numPr()
            numpr.get_or_add_ilvl().val = 0
            numpr.get_or_add_numId().val = self._num_ids[key]

    def _new_num_instance(self, para) -> int:
        """Eigene Zählung je Liste, damit „1.“ neu beginnt."""
        numbering = self.d.part.numbering_part.element
        base = None
        for s in (para.style, para.style.base_style):
            if s is not None and s.element.pPr is not None and s.element.pPr.numPr is not None:
                base = s.element.pPr.numPr.numId.val
                break
        if base is None:
            return 1
        src = numbering.xpath(f'w:num[@w:numId="{base}"]')[0]
        abs_id = src.xpath("w:abstractNumId/@w:val")[0]
        new_id = max([int(n) for n in numbering.xpath("w:num/@w:numId")] + [0]) + 1
        num = OxmlElement("w:num")
        num.set(qn("w:numId"), str(new_id))
        an = OxmlElement("w:abstractNumId")
        an.set(qn("w:val"), abs_id)
        num.append(an)
        ov = OxmlElement("w:lvlOverride")
        ov.set(qn("w:ilvl"), "0")
        so = OxmlElement("w:startOverride")
        so.set(qn("w:val"), "1")
        ov.append(so)
        num.append(ov)
        numbering.append(num)
        return new_id

    # ---- Läufe ----------------------------------------------------------
