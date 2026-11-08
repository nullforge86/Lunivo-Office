"""DOCX lesen: Absatz – fachlich gekapselte Verarbeitung."""
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

class LesenAbsatzMixin:
    """Fachliche Teilverantwortung des DOCX-Readers."""

    def _block_format(self, para: Paragraph) -> QTextBlockFormat:
        pf = para.paragraph_format
        st = self._ps(para)
        b = QTextBlockFormat()

        def sicher(fn, *a):
            try:
                return fn(*a)
            except (ValueError, KeyError, AttributeError):        # ungewöhnliche Werte (z. B. jc="start")
                return None

        def eff(getter):
            v = sicher(getter, pf)
            if v is None and st is not None:
                v = self._style_attr(st, lambda s: sicher(getter, s.paragraph_format))
            return v

        ppr = para._p.pPr
        if ppr is not None and ppr.find(qn("w:bidi")) is not None:
            b.setLayoutDirection(Qt.RightToLeft)
        b.setAlignment(self._ausrichtung(para, st))
        left = eff(lambda p: p.left_indent)
        right = eff(lambda p: p.right_indent)
        first = eff(lambda p: p.first_line_indent)
        if left is not None:
            lpx = _emu_to_px(left)
            info = self._list_info(para)
            if info is not None and lpx > 0:                          # Qt rückt Listenabsätze selbst um 40 px je Ebene ein
                lpx = max(0.0, lpx - 40.0 * (info[1] + 1))
            b.setLeftMargin(lpx)
        if right is not None:
            b.setRightMargin(_emu_to_px(right))
        if first is not None:
            hanging_liste = first < 0 and self._list_info(para) is not None
            # Hängender Einzug einer Liste: Das Zeichen steht links vom Text, alle Zeilen beginnen bei „links“ — Qt setzt das Zeichen selbst
            # vor den Text; ein negativer Erstzeileneinzug würde die erste Zeile gegenüber den folgenden verschieben.
            b.setTextIndent(0 if hanging_liste else _emu_to_px(first))
        sb = eff(lambda p: p.space_before)
        sa = eff(lambda p: p.space_after)
        b.setTopMargin(_pt_to_px(sb.pt) if sb is not None else 0)
        b.setBottomMargin(_pt_to_px(sa.pt) if sa is not None else 0)
        sp = ppr.find(qn("w:spacing")) if ppr is not None else None
        leer = not "".join(para._p.xpath(".//w:t/text()")).strip() if hasattr(para._p, "xpath") else False
        if sp is not None and not leer:                               # „Automatisch“ (aus Webseiten): 14 pt davor/danach; leere Absätze behalten nur ihre Höhe
            wahr = ("1", "true", "on")
            if (sp.get(qn("w:beforeAutospacing")) or "").lower() in wahr:
                b.setTopMargin(_pt_to_px(14.0))
            if (sp.get(qn("w:afterAutospacing")) or "").lower() in wahr:
                b.setBottomMargin(_pt_to_px(14.0))
        ls = eff(lambda p: p.line_spacing)
        if ls is not None:
            if isinstance(ls, float) or (isinstance(ls, int) and ls < 100):
                b.setLineHeight(float(ls) * 100, LH_PROPORTIONAL)
            else:  # Length in EMU → feste Höhe
                pt = ls.pt
                b.setLineHeight(pt / PT_PER_PX, LH_FIXED)
        if eff(lambda p: p.page_break_before) or self.pending_break:
            b.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
            if self.pending_break and getattr(self, "pending_col", False):
                b.setProperty(B_SPALTE, 1)
            self.pending_break = False
            self.pending_col = False
        shd = para._p.xpath("w:pPr/w:shd")
        art = muster.schluessel_von_ooxml(shd[0].get(qn("w:val"))) if shd else None
        if shd and art and art != "loeschen":                    # Muster über Füllfarbe
            farbe = shd[0].get(qn("w:color"))
            fill = shd[0].get(qn("w:fill"))
            mf = "#" + farbe if farbe not in (None, "auto") else Farbe.SCHWARZ
            ff = "#" + fill if fill not in (None, "auto") else None
            b.setBackground(muster.pinsel(art, mf, ff))
            b.setProperty(B_MUSTER, muster.als_text(art, mf, ff))
        elif shd and shd[0].get(qn("w:fill")) not in (None, "auto"):
            b.setBackground(QBrush(QColor("#" + shd[0].get(qn("w:fill")))))
        from lunivo_writer.editor import absatzopt
        opt = absatzopt.aus_ppr(para._p.pPr)
        if opt:
            absatzopt.setzen(b, {**absatzopt.VORGABE, **opt})
        stops = list(pf.tab_stops)
        if stops:
            from docx.enum.text import WD_TAB_ALIGNMENT
            from PySide6.QtGui import QTextOption
            art = {WD_TAB_ALIGNMENT.RIGHT: QTextOption.RightTab, WD_TAB_ALIGNMENT.CENTER: QTextOption.CenterTab,
                   WD_TAB_ALIGNMENT.DECIMAL: QTextOption.DelimiterTab}
            b.setTabPositions([QTextOption.Tab(_emu_to_px(t.position), art.get(t.alignment, QTextOption.LeftTab))
                               for t in stops])
            from docx.enum.text import WD_TAB_LEADER
            from lunivo_writer.editor import tabfuell
            lk = {WD_TAB_LEADER.DOTS: "punkt", WD_TAB_LEADER.DASHES: "strich", WD_TAB_LEADER.LINES: "linie", WD_TAB_LEADER.MIDDLE_DOT: "mitte"}
            tabfuell.setzen(b, {round(_emu_to_px(t.position), 2): lk[t.leader] for t in stops if t.leader in lk})
        lvl = self._heading_level(para)
        if lvl:
            b.setHeadingLevel(lvl)
        if st is not None and st.name in ("Title", "Subtitle", "Quote", "No Spacing"):
            b.setProperty(STYLE_PROP, st.name)
        elif st is not None and not lvl and not st.builtin and st.name != "Normal":
            self._eigene_vorlage(st, b)
        if para._p.xpath("w:pPr/w:sectPr"):                       # letzter Absatz eines Abschnitts: der folgende Abschnitt wird hier beschrieben
            from lunivo_writer.editor import abschnitte as AB
            k, secs = self._ab_zaehler, self.d.sections
            self._ab_zaehler += 1
            if k + 1 < len(secs):
                nxt = secs[k + 1]
                b.setProperty(AB.B_ABSCHNITT, AB.eintrag(self._abschnitt_beginn(nxt), self._section_page(nxt, basis=self._erste_seite)))
        return b

    # ---- Listen ------------------------------------------------------

    def _list_info(self, para: Paragraph):
        """→ (numId, ilvl, 'bullet'|'decimal'|…) oder None."""
        ppr = para._p.pPr
        numpr = ppr.numPr if ppr is not None else None
        num_id = ilvl = None
        if numpr is not None:
            num_id = numpr.numId.val if numpr.numId is not None else None
            ilvl = numpr.ilvl.val if numpr.ilvl is not None else 0
        if num_id is None and self._ps(para) is not None:
            for s in self._kette(self._ps(para)):
                sp = s.element.pPr
                if sp is not None and sp.numPr is not None and sp.numPr.numId is not None:
                    num_id = sp.numPr.numId.val
                    ilvl = sp.numPr.ilvl.val if sp.numPr.ilvl is not None else 0
                    break
        if not num_id:
            return None
        fmt = self._num_format(num_id, ilvl or 0)
        return num_id, ilvl or 0, fmt

    def _num_format(self, num_id, ilvl) -> str:
        try:
            numbering = self.d.part.numbering_part.element
        except Exception:
            return "bullet"
        num = numbering.xpath(f'w:num[@w:numId="{num_id}"]')
        if not num:
            return "bullet"
        abs_id = num[0].xpath("w:abstractNumId/@w:val")
        if not abs_id:
            return "bullet"
        lv = numbering.xpath(
            f'w:abstractNum[@w:abstractNumId="{abs_id[0]}"]/w:lvl[@w:ilvl="{ilvl}"]/w:numFmt/@w:val')
        return lv[0] if lv else "decimal"

    _QT_LIST = {
        "bullet": QTextListFormat.ListDisc,
        "decimal": QTextListFormat.ListDecimal,
        "lowerLetter": QTextListFormat.ListLowerAlpha,
        "upperLetter": QTextListFormat.ListUpperAlpha,
        "lowerRoman": QTextListFormat.ListLowerRoman,
        "upperRoman": QTextListFormat.ListUpperRoman,
    }

    # ---- Einfügen ----------------------------------------------------

    def _start_block(self, bfmt: QTextBlockFormat, cfmt: QTextCharFormat, cursor: QTextCursor, reuse: bool):
        if reuse:
            cursor.setBlockFormat(bfmt)
            cursor.setBlockCharFormat(cfmt)
        else:
            cursor.insertBlock(bfmt, cfmt)

    def add_paragraph(self, para: Paragraph, cursor: QTextCursor, reuse: bool, in_table=False):
        bfmt = self._block_format(para)
        self._block_zusatz(bfmt, para)
        base_cfmt = QTextCharFormat()
        base_cfmt.setFontFamilies([self._font_name(_NoRun(), para)])
        base_cfmt.setFontPointSize(self._font_size_pt(_NoRun(), para))
        sz = _xp(para._p, "w:pPr/w:rPr/w:sz/@w:val")                       # Schrift des Absatzzeichens: sie bestimmt die Höhe leerer Absätze
        if sz and sz[0].isdigit():
            base_cfmt.setFontPointSize(int(sz[0]) / 2.0)
        self._start_block(bfmt, base_cfmt, cursor, reuse)

        info = None if in_table else self._list_info(para)
        if info is not None:
            num_id, ilvl, kind = info
            lf = QTextListFormat()
            lf.setStyle(self._QT_LIST.get(kind, QTextListFormat.ListDisc))
            lf.setIndent(ilvl + 1)
            key = (num_id, ilvl)
            if self.last_list and self.last_list[0] == key:
                self.last_list[1].add(cursor.block())
            else:
                self.last_list = (key, cursor.createList(lf))
        else:
            self.last_list = None

        self.deferred_break = False
        had_content = False
        had_content |= self._laufe(para._p, para, cursor)
        if self.deferred_break:
            # Umbruch am Absatzende: er gilt für den nächsten Absatz
            self.deferred_break = False
            self.pending_break = True
            self.pending_col = getattr(self, "deferred_col", False)
            return not had_content        # leerer Absatz → Block wiederverwenden
        return False

    def _laufe(self, eltern, para, cursor: QTextCursor, href: Optional[str] = None) -> bool:
        """Kinder eines Absatzes der Reihe nach: Läufe, Links, nachverfolgte Änderungen, Kommentar- und Textmarkenbereiche."""
        had = False
        for el in eltern:
            tag = el.tag
            if tag == qn("w:r"):
                had |= self._add_run(Run(el, para), para, cursor, href=href)
            elif tag == qn("w:hyperlink"):
                h = Hyperlink(el, para)
                url = h.url or ("#" + h.fragment if h.fragment else "")
                alt_tipp, self._link_tipp = getattr(self, "_link_tipp", ""), el.get(qn("w:tooltip")) or ""
                had |= self._laufe(el, para, cursor, href=url)
                self._link_tipp = alt_tipp
            elif tag in (qn("w:ins"), qn("w:del")):
                alt = self._aend
                self._aend = ("ins" if tag == qn("w:ins") else "del", el.get(qn("w:author")) or "", el.get(qn("w:date")) or "")
                had |= self._laufe(el, para, cursor, href=href)
                self._aend = alt
            elif tag == qn("w:commentRangeStart"):
                self._komm_offen.append(int(el.get(qn("w:id"))))
            elif tag == qn("w:commentRangeEnd"):
                i = int(el.get(qn("w:id")))
                if i in self._komm_offen:
                    self._komm_offen.remove(i)
            elif tag == qn("w:bookmarkStart"):
                n = el.get(qn("w:name")) or ""
                if n and not n.startswith("_"):
                    self._lz_offen[el.get(qn("w:id"))] = n
                    self._lz_pos[el.get(qn("w:id"))] = cursor.position()
            elif tag == qn("w:bookmarkEnd"):
                i = el.get(qn("w:id"))
                n = self._lz_offen.pop(i, None)
                if n is not None and self._lz_pos.pop(i, None) == cursor.position():
                    self._lz_wartend.append(n)         # leere Textmarke: hängt am folgenden Text
            elif tag in (qn("w:sdt"),):
                inhalt = el.find(qn("w:sdtContent"))
                if inhalt is not None:
                    alt_form, self._form = self._form, self._form_meta(el) or self._form
                    had |= self._laufe(inhalt, para, cursor, href=href)
                    self._form = alt_form
            elif tag == qn("w:fldSimple"):
                self._feld = {"instr": el.get(qn("w:instr")) or "", "phase": "r"}
                had |= self._laufe(el, para, cursor, href=href)
                self._feld_ende()
            elif tag == qn("w:smartTag"):
                had |= self._laufe(el, para, cursor, href=href)
        return had

    FELDER_BEHALTEN = ("SEQ", "CITATION")

    def _feld_ende(self) -> None:
        f, self._feld = self._feld, None
        if not f:
            return
        teile = f["instr"].split()
        if teile and teile[0].upper() == "XE" and self._letzter:
            from lunivo_writer.editor.indexeintrag import aus_feld
            from lunivo_writer.editor.zusatz import P_INDEX_OPT
            e = aus_feld(f["instr"])
            if e is None:
                return
            c = QTextCursor(self.doc)
            c.setPosition(self._letzter[0]); c.setPosition(self._letzter[1], QTextCursor.KeepAnchor)
            nf = QTextCharFormat(); nf.setProperty(P_INDEX, e.text())
            if e.schalter():
                nf.setProperty(P_INDEX_OPT, e.schalter())
            c.mergeCharFormat(nf)

    def _form_meta(self, sdt) -> str:
        """Inhaltssteuerelement → Formularfeld-Daten (JSON); eigene Felder tragen sie im Tag, fremde (Word) werden aus der Art abgeleitet."""
        from lunivo_writer.editor import formular as FO
        pr = sdt.find(qn("w:sdtPr"))
        if pr is None:
            return ""
        tag = pr.find(qn("w:tag"))
        t = tag.get(qn("w:val")) if tag is not None else ""
        if t and t.startswith("lunivo:"):
            m = FO.meta_lesen(t[len("lunivo:"):])
            if m:
                return FO.meta_text(m)
        al = pr.find(qn("w:alias"))
        name = al.get(qn("w:val")) if al is not None else ""
        leer = pr.find(qn("w:showingPlcHdr")) is not None
        if pr.find(qn("w:dropDownList")) is not None or pr.find(qn("w:comboBox")) is not None:
            liste = pr.find(qn("w:dropDownList"))
            if liste is None:
                liste = pr.find(qn("w:comboBox"))
            opt = [li.get(qn("w:displayText")) or li.get(qn("w:value")) or "" for li in liste.findall(qn("w:listItem"))]
            m = FO.meta("auswahl", name, optionen=[o for o in opt if o])
        elif pr.find(qn("w:date")) is not None:
            m = FO.meta("datum", name)
        elif any(el.tag.endswith("}checkbox") for el in pr):
            m = FO.meta("kasten", name)
        elif pr.find(qn("w:text")) is not None:
            m = FO.meta("text", name)
        else:
            return ""
        if leer:
            m["leer"] = True
        return FO.meta_text(m)

    def _zusatz_formate(self, cfmt: QTextCharFormat) -> None:
        if self._feld and self._feld["phase"] == "r":
            teile = self._feld["instr"].split()
            if teile and teile[0].upper() in self.FELDER_BEHALTEN:
                cfmt.setProperty(P_FELD, self._feld["instr"].strip())
                if teile[0].upper() == "CITATION" and len(teile) > 1:
                    cfmt.setProperty(P_ZITAT, teile[1])
        if self._komm_offen:
            cfmt.setProperty(P_KOMMENTAR, self._komm_offen[-1])
        if self._form:
            cfmt.setProperty(P_FORM, self._form)
        if self._aend:
            cfmt.setProperty(P_AENDERUNG, self._aend[0])
            cfmt.setProperty(P_AUTOR, self._aend[1])
            cfmt.setProperty(P_DATUM, self._aend[2])
        namen = list(self._lz_offen.values()) + self._lz_wartend
        if namen and not cfmt.isAnchor():
            cfmt.setAnchor(True)
            cfmt.setAnchorNames(namen)

    _TOC_STILE = {"TOC Heading": "kopf", **{f"TOC {i}": f"zeile{i}" for i in range(1, 10)}, "Table of Figures": "zeile1",
                  "Index 1": "zeile1", "Index 2": "zeile2", "Bibliography": "zeile1"}

    def _block_zusatz(self, bfmt: QTextBlockFormat, para: Paragraph) -> None:
        """Verzeichnis- und Beschriftungsabsätze an ihrer Formatvorlage wiedererkennen; Absatzrahmen aus w:pBdr."""
        ppr = para._p.pPr
        bdr = ppr.find(qn("w:pBdr")) if ppr is not None else None
        if bdr is not None:
            da = [(kurz, bdr.find(qn(f"w:{x}"))) for x, kurz in (("top", "t"), ("left", "l"), ("bottom", "b"), ("right", "r"), ("between", "h"))]
            da = [(k, e) for k, e in da if e is not None and e.get(qn("w:val"), "nil") not in ("nil", "none")]
            if da:
                e = da[0][1]
                col = e.get(qn("w:color")) or "000000"
                art = art_aus_docx(e.get(qn("w:val")))
                li = Linie(f"#{col.lower() if col.lower() != 'auto' else '000000'}", int(e.get(qn("w:sz")) or 8) / 8, art).mit_seiten("".join(k for k, _e in da))
                abst = {k: e2.get(qn("w:space")) for k, e2 in da}
                if any(v not in (None, "4") for v in abst.values()):          # eigener Abstand zum Text (w:space in pt)
                    li.abstand = ",".join(str(int(abst.get(k) or 4)) for k in "tblr")
                bfmt.setProperty(B_RAHMEN, li.text())
        try:
            name = self._ps(para).name
        except Exception:
            return
        if name in self._TOC_STILE:
            art = "toc" if name.startswith("TOC ") else {"Index 1": "index", "Index 2": "index", "Bibliography": "lit"}.get(name)
            if name == "Table of Figures":
                art = "tab" if para.text.strip().lower().startswith(("tabelle", "table")) else "abb"
            elif name == "TOC Heading":
                nxt = para._p.getnext()
                art = "toc"
                if nxt is not None and nxt.tag == qn("w:p"):
                    nn = Paragraph(nxt, para._parent).style.name
                    art = {"Table of Figures": "abb", "Index 1": "index", "Bibliography": "lit"}.get(nn, "toc")
                    if nn == "Table of Figures" and Paragraph(nxt, para._parent).text.strip().lower().startswith(("tabelle", "table")):
                        art = "tab"
            bfmt.setProperty(B_TOC, self._TOC_STILE[name])
            bfmt.setProperty(B_ART, art or "toc")
        elif name == "Caption":
            erstes = para.text.strip().split(" ")[0] if para.text.strip() else ""
            bfmt.setProperty(B_CAP, erstes if erstes in BESCHRIFTUNGEN else (erstes or "Abbildung"))

    def _flush_break(self, cursor: QTextCursor):
        if self.deferred_break:
            self.deferred_break = False
            cursor.insertBlock()
            bf = cursor.blockFormat()
            bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
            if getattr(self, "deferred_col", False):
                bf.setProperty(B_SPALTE, 1)
                self.deferred_col = False
            cursor.setBlockFormat(bf)
