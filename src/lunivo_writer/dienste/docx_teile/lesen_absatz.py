"""DOCX lesen: Absatz – fachlich gekapselte Verarbeitung."""
from __future__ import annotations

from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
from PySide6.QtGui import QTextOption

from lunivo_writer.dienste.docx_teile.lesen_gemeinsam import (  # noqa: F401
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
    LH_MIN,
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

# Tabstopp: DOCX → Qt (Art) und Füllzeichen → Lunivo-Schlüssel
_TAB_ART = {WD_TAB_ALIGNMENT.RIGHT: QTextOption.RightTab, WD_TAB_ALIGNMENT.CENTER: QTextOption.CenterTab,
            WD_TAB_ALIGNMENT.DECIMAL: QTextOption.DelimiterTab}
_TAB_FUELLUNG = {WD_TAB_LEADER.DOTS: "punkt", WD_TAB_LEADER.DASHES: "strich", WD_TAB_LEADER.LINES: "linie", WD_TAB_LEADER.MIDDLE_DOT: "mitte"}


# Kindelemente eines Absatzes → Methode, die sie liest (nicht aufgeführte werden übergangen)
_LAUF_ELEMENTE = {
    qn("w:r"): "_lauf_run", qn("w:hyperlink"): "_lauf_hyperlink", qn("w:ins"): "_lauf_aenderung", qn("w:del"): "_lauf_aenderung",
    qn("w:commentRangeStart"): "_lauf_kommentar_start", qn("w:commentRangeEnd"): "_lauf_kommentar_ende",
    qn("w:bookmarkStart"): "_lauf_textmarke_start", qn("w:bookmarkEnd"): "_lauf_textmarke_ende",
    qn("w:sdt"): "_lauf_steuerelement", qn("w:fldSimple"): "_lauf_feld_einfach", qn("w:smartTag"): "_lauf_durchreichen",
}

# Rahmenseiten (DOCX-Name, Kürzel)
_RAHMEN_SEITEN = (("top", "t"), ("left", "l"), ("bottom", "b"), ("right", "r"), ("between", "h"))


def _listeneintraege(liste) -> list:
    """Anzeigetexte der Einträge einer Auswahlliste (w:listItem), ersatzweise deren Werte."""
    return [li.get(qn("w:displayText")) or li.get(qn("w:value")) or "" for li in liste.findall(qn("w:listItem"))]


class LesenAbsatzMixin:
    """Fachliche Teilverantwortung des DOCX-Readers."""

    @staticmethod
    def _sicher(fn, *a):
        try:
            return fn(*a)
        except (ValueError, KeyError, AttributeError):        # ungewöhnliche Werte (z. B. jc="start")
            return None

    def _para_attr(self, getter, pf, st):
        """Absatzeigenschaft: direkt am Absatz, sonst aus der Formatvorlage (samt Vorlagenkette)."""
        v = self._sicher(getter, pf)
        if v is None and st is not None:
            v = self._style_attr(st, lambda s: self._sicher(getter, s.paragraph_format))
        tab = getattr(self, "_tabellen_stil", None)
        if v is None and tab is not None:                  # Absatz in einer Tabelle: die Tabellenvorlage gilt vor den Vorgaben des Dokuments
            v = self._style_attr(tab, lambda s: self._sicher(getter, s.paragraph_format))
        return v

    def _block_format(self, para: Paragraph) -> QTextBlockFormat:
        pf = para.paragraph_format
        st = self._ps(para)
        b = QTextBlockFormat()

        def eff(getter):
            return self._para_attr(getter, pf, st)

        ppr = para._p.pPr
        if ppr is not None and ppr.find(qn("w:bidi")) is not None:
            b.setLayoutDirection(Qt.RightToLeft)
        b.setAlignment(self._ausrichtung(para, st))
        self._bf_einzuege(b, para, eff)
        self._bf_abstaende(b, para, ppr, eff)
        if eff(lambda p: p.page_break_before) or self.pending_break:
            self._bf_seitenumbruch(b)
        self._bf_schattierung(b, para)
        from lunivo_writer.editor.seite import absatzopt
        opt = absatzopt.aus_ppr(para._p.pPr)
        if opt:
            absatzopt.setzen(b, {**absatzopt.VORGABE, **opt})
        self._bf_tabs(b, pf)
        self._bf_vorlage(b, para, st)
        self._bf_abschnitt(b, para)
        return b

    def _bf_einzuege(self, b: QTextBlockFormat, para: Paragraph, eff) -> None:
        """Links-, Rechts- und Erstzeileneinzug (Listenabsätze: Qt rückt selbst ein)."""
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

    def _bf_abstaende(self, b: QTextBlockFormat, para: Paragraph, ppr, eff) -> None:
        """Abstand davor/danach (auch „Automatisch“ aus Webseiten), danach der Zeilenabstand."""
        sb = eff(lambda p: p.space_before)
        sa = eff(lambda p: p.space_after)
        b.setTopMargin(_pt_to_px(sb.pt) if sb is not None else 0)
        b.setBottomMargin(_pt_to_px(sa.pt) if sa is not None else 0)
        self._bf_automatisch(b, para, ppr)
        self._bf_zeilenabstand(b, eff)

    @staticmethod
    def _bf_automatisch(b: QTextBlockFormat, para: Paragraph, ppr) -> None:
        """„Automatisch“ (aus Webseiten): 14 pt davor/danach; leere Absätze behalten nur ihre Höhe."""
        sp = ppr.find(qn("w:spacing")) if ppr is not None else None
        leer = not "".join(para._p.xpath(".//w:t/text()")).strip() if hasattr(para._p, "xpath") else False
        if sp is None or leer:
            return
        wahr = ("1", "true", "on")
        if (sp.get(qn("w:beforeAutospacing")) or "").lower() in wahr:
            b.setTopMargin(_pt_to_px(14.0))
        if (sp.get(qn("w:afterAutospacing")) or "").lower() in wahr:
            b.setBottomMargin(_pt_to_px(14.0))

    @staticmethod
    def _bf_zeilenabstand(b: QTextBlockFormat, eff) -> None:
        ls = eff(lambda p: p.line_spacing)
        if ls is not None:
            if isinstance(ls, float) or (isinstance(ls, int) and ls < 100):
                b.setLineHeight(float(ls) * 100, LH_PROPORTIONAL)
            else:  # Length in EMU → feste Höhe; „mindestens“ (w:lineRule="atLeast") wächst mit hohen Zeilen, zum Beispiel mit einem Bild in der Zeile
                from docx.enum.text import WD_LINE_SPACING
                mindestens = eff(lambda p: p.line_spacing_rule) == WD_LINE_SPACING.AT_LEAST
                b.setLineHeight(ls.pt / PT_PER_PX, LH_MIN if mindestens else LH_FIXED)

    def _bf_seitenumbruch(self, b: QTextBlockFormat) -> None:
        """Seiten- (und ggf. Spalten-)Umbruch vor dem Absatz; ein vorgemerkter Umbruch ist damit verbraucht."""
        b.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
        if self.pending_break and getattr(self, "pending_col", False):
            b.setProperty(B_SPALTE, 1)
        self.pending_break = False
        self.pending_col = False

    @staticmethod
    def _bf_schattierung(b: QTextBlockFormat, para: Paragraph) -> None:
        """Absatzhintergrund aus w:shd: Muster über Füllfarbe oder einfache Füllfarbe."""
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

    @staticmethod
    def _bf_tabs(b: QTextBlockFormat, pf) -> None:
        """Tabstopps mit Art und Füllzeichen."""
        stops = list(pf.tab_stops)
        if not stops:
            return
        from lunivo_writer.editor.text import tabfuell
        b.setTabPositions([QTextOption.Tab(_emu_to_px(t.position), _TAB_ART.get(t.alignment, QTextOption.LeftTab)) for t in stops])
        tabfuell.setzen(b, {round(_emu_to_px(t.position), 2): _TAB_FUELLUNG[t.leader] for t in stops if t.leader in _TAB_FUELLUNG})

    def _bf_vorlage(self, b: QTextBlockFormat, para: Paragraph, st) -> None:
        """Überschriftenebene, Standardvorlage (Titel, Zitat …) oder eigene Formatvorlage."""
        lvl = self._heading_level(para)
        if lvl:
            b.setHeadingLevel(lvl)
        if st is not None and st.name in ("Title", "Subtitle", "Quote", "No Spacing"):
            b.setProperty(STYLE_PROP, st.name)
        elif st is not None and not lvl and not st.builtin and st.name != "Normal":
            self._eigene_vorlage(st, b)

    def _bf_abschnitt(self, b: QTextBlockFormat, para: Paragraph) -> None:
        """Letzter Absatz eines Abschnitts: der folgende Abschnitt wird hier beschrieben."""
        if para._p.xpath("w:pPr/w:sectPr"):
            from lunivo_writer.editor.seite import abschnitte as AB
            k, secs = self._ab_zaehler, self.d.sections
            self._ab_zaehler += 1
            if k + 1 < len(secs):
                nxt = secs[k + 1]
                b.setProperty(AB.B_ABSCHNITT, AB.eintrag(self._abschnitt_beginn(nxt), self._section_page(nxt, basis=self._erste_seite)))

    # ---- Listen ------------------------------------------------------

    def _list_info(self, para: Paragraph):
        """→ (numId, ilvl, 'bullet'|'decimal'|…) oder None."""
        num_id, ilvl = self._numpr_direkt(para)
        if num_id is None and self._ps(para) is not None:
            num_id, ilvl = self._numpr_aus_vorlage(self._ps(para))
        if not num_id:
            return None
        fmt = self._num_format(num_id, ilvl or 0)
        return num_id, ilvl or 0, fmt

    @staticmethod
    def _numpr_direkt(para: Paragraph):
        """(numId, ilvl) aus w:numPr des Absatzes, sonst (None, None)."""
        ppr = para._p.pPr
        numpr = ppr.numPr if ppr is not None else None
        if numpr is None:
            return None, None
        return (numpr.numId.val if numpr.numId is not None else None), (numpr.ilvl.val if numpr.ilvl is not None else 0)

    def _numpr_aus_vorlage(self, stil):
        """(numId, ilvl) aus der ersten Formatvorlage der Kette mit Nummerierung, sonst (None, None)."""
        for s in self._kette(stil):
            sp = s.element.pPr
            if sp is not None and sp.numPr is not None and sp.numPr.numId is not None:
                return sp.numPr.numId.val, (sp.numPr.ilvl.val if sp.numPr.ilvl is not None else 0)
        return None, None

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

    @staticmethod
    def _block_format_setzen(block, vf: QTextBlockFormat) -> None:
        """Das Format eines schon geschriebenen Absatzes ändern (der Modell-Leser überschreibt das: sein Absatz ist kein ``QTextBlock``)."""
        QTextCursor(block).setBlockFormat(vf)

    def _start_block(self, bfmt: QTextBlockFormat, cfmt: QTextCharFormat, cursor: QTextCursor, reuse: bool):
        if reuse:
            cursor.setBlockFormat(bfmt)
            cursor.setBlockCharFormat(cfmt)
        else:
            cursor.insertBlock(bfmt, cfmt)

    def _kontext_abstand(self, para: Paragraph) -> bool:
        """w:contextualSpacing: kein Abstand zwischen Absätzen derselben Vorlage (Word-Regel, Listen typisch)."""
        ppr = para._p.pPr
        el = ppr.find(qn("w:contextualSpacing")) if ppr is not None else None
        if el is None:
            el = self._style_attr(self._ps(para), lambda s: s.element.find(qn("w:pPr") + "/" + qn("w:contextualSpacing")))
        if el is None:
            return False
        return (el.get(qn("w:val")) or "1").lower() not in ("0", "false", "off")

    def add_paragraph(self, para: Paragraph, cursor: QTextCursor, reuse: bool, in_table=False):
        bfmt = self._block_format(para)
        self._block_zusatz(bfmt, para)
        name = self._ps_name(para)
        # Kontextabstand: Abstand zwischen zwei aufeinanderfolgenden Absätzen gleicher Vorlage entfällt (davor und danach)
        gleich = (not reuse and not in_table and getattr(self, "_letzter_stil", None) == name and self._kontext_abstand(para))
        vorher = cursor.block() if gleich else None
        if gleich:
            bfmt.setTopMargin(0)
        self._letzter_stil = None if in_table else name
        base_cfmt = QTextCharFormat()
        base_cfmt.setFontFamilies([self._font_name(_NoRun(), para)])
        base_cfmt.setFontPointSize(self._font_size_pt(_NoRun(), para))
        sz = _xp(para._p, "w:pPr/w:rPr/w:sz/@w:val")                       # Schrift des Absatzzeichens: sie bestimmt die Höhe leerer Absätze
        if sz and sz[0].isdigit():
            base_cfmt.setFontPointSize(int(sz[0]) / 2.0)
        self._start_block(bfmt, base_cfmt, cursor, reuse)
        if vorher is not None and vorher.isValid():                 # der vorige Absatz verliert seinen Abstand danach
            vf = vorher.blockFormat()
            vf.setBottomMargin(0)
            self._block_format_setzen(vorher, vf)

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
            handler = _LAUF_ELEMENTE.get(el.tag)
            if handler:
                had |= bool(getattr(self, handler)(el, para, cursor, href))
        return had

    def _lauf_run(self, el, para, cursor, href) -> bool:
        return self._add_run(Run(el, para), para, cursor, href=href)

    def _lauf_hyperlink(self, el, para, cursor, href) -> bool:
        h = Hyperlink(el, para)
        url = h.url or ("#" + h.fragment if h.fragment else "")
        alt_tipp, self._link_tipp = getattr(self, "_link_tipp", ""), el.get(qn("w:tooltip")) or ""
        had = self._laufe(el, para, cursor, href=url)
        self._link_tipp = alt_tipp
        return had

    def _lauf_aenderung(self, el, para, cursor, href) -> bool:
        """Nachverfolgte Änderung (w:ins / w:del): Art, Autor und Datum gelten für die enthaltenen Läufe."""
        alt = self._aend
        self._aend = ("ins" if el.tag == qn("w:ins") else "del", el.get(qn("w:author")) or "", el.get(qn("w:date")) or "")
        had = self._laufe(el, para, cursor, href=href)
        self._aend = alt
        return had

    def _lauf_kommentar_start(self, el, para, cursor, href) -> bool:
        self._komm_offen.append(int(el.get(qn("w:id"))))
        return False

    def _lauf_kommentar_ende(self, el, para, cursor, href) -> bool:
        i = int(el.get(qn("w:id")))
        if i in self._komm_offen:
            self._komm_offen.remove(i)
        return False

    def _lauf_textmarke_start(self, el, para, cursor, href) -> bool:
        n = el.get(qn("w:name")) or ""
        if n and not n.startswith("_"):
            self._lz_offen[el.get(qn("w:id"))] = n
            self._lz_pos[el.get(qn("w:id"))] = cursor.position()
        return False

    def _lauf_textmarke_ende(self, el, para, cursor, href) -> bool:
        i = el.get(qn("w:id"))
        n = self._lz_offen.pop(i, None)
        if n is not None and self._lz_pos.pop(i, None) == cursor.position():
            self._lz_wartend.append(n)         # leere Textmarke: hängt am folgenden Text
        return False

    def _lauf_steuerelement(self, el, para, cursor, href) -> bool:
        inhalt = el.find(qn("w:sdtContent"))
        if inhalt is None:
            return False
        alt_form, self._form = self._form, self._form_meta(el) or self._form
        had = self._laufe(inhalt, para, cursor, href=href)
        self._form = alt_form
        return had

    def _lauf_feld_einfach(self, el, para, cursor, href) -> bool:
        self._feld = {"instr": el.get(qn("w:instr")) or "", "phase": "r"}
        had = self._laufe(el, para, cursor, href=href)
        self._feld_ende()
        return had

    def _lauf_durchreichen(self, el, para, cursor, href) -> bool:
        return self._laufe(el, para, cursor, href=href)

    FELDER_BEHALTEN = ("SEQ", "CITATION")

    def _feld_ende(self) -> None:
        f, self._feld = self._feld, None
        if not f:
            return
        teile = f["instr"].split()
        if teile and teile[0].upper() == "XE" and self._letzter:
            from lunivo_writer.editor.dokument.indexeintrag import aus_feld
            from lunivo_writer.editor.dokument.zusatz import P_INDEX_OPT
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
        """Inhaltssteuerelement → Formularfeld-Daten (JSON); eigene Felder tragen sie im Tag, fremde (aus anderen Programmen) werden aus der Art abgeleitet."""
        from lunivo_writer.editor.dokument import formular as FO
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
        m = self._form_meta_fremd(pr, al.get(qn("w:val")) if al is not None else "")
        if m is None:
            return ""
        if pr.find(qn("w:showingPlcHdr")) is not None:
            m["leer"] = True
        return FO.meta_text(m)

    @staticmethod
    def _form_meta_fremd(pr, name: str):
        """Art des fremden Steuerelements (Auswahl, Datum, Kontrollkästchen, Text) → Formularfeld-Daten oder None."""
        from lunivo_writer.editor.dokument import formular as FO
        liste = pr.find(qn("w:dropDownList"))
        if liste is None:
            liste = pr.find(qn("w:comboBox"))
        if liste is not None:
            return FO.meta("auswahl", name, optionen=[o for o in _listeneintraege(liste) if o])
        art = next((a for a, vorhanden in (("datum", pr.find(qn("w:date")) is not None),
                                           ("kasten", any(el.tag.endswith("}checkbox") for el in pr)),
                                           ("text", pr.find(qn("w:text")) is not None)) if vorhanden), None)
        return FO.meta(art, name) if art else None

    def _zusatz_formate(self, cfmt: QTextCharFormat) -> None:
        self._zusatz_feld(cfmt)
        if self._komm_offen:
            cfmt.setProperty(P_KOMMENTAR, self._komm_offen[-1])
        if self._form:
            cfmt.setProperty(P_FORM, self._form)
        self._zusatz_aenderung(cfmt)
        namen = list(self._lz_offen.values()) + self._lz_wartend
        if namen and not cfmt.isAnchor():
            cfmt.setAnchor(True)
            cfmt.setAnchorNames(namen)

    def _zusatz_aenderung(self, cfmt: QTextCharFormat) -> None:
        """Nachverfolgte Änderung: Art, Autor, Datum."""
        if self._aend:
            cfmt.setProperty(P_AENDERUNG, self._aend[0])
            cfmt.setProperty(P_AUTOR, self._aend[1])
            cfmt.setProperty(P_DATUM, self._aend[2])

    def _zusatz_feld(self, cfmt: QTextCharFormat) -> None:
        """Felder, die erhalten bleiben (SEQ, CITATION): Anweisung (und Zitatschlüssel) am Zeichenformat."""
        if self._feld and self._feld["phase"] == "r":
            teile = self._feld["instr"].split()
            if teile and teile[0].upper() in self.FELDER_BEHALTEN:
                cfmt.setProperty(P_FELD, self._feld["instr"].strip())
                if teile[0].upper() == "CITATION" and len(teile) > 1:
                    cfmt.setProperty(P_ZITAT, teile[1])

    _TOC_STILE = {"TOC Heading": "kopf", **{f"TOC {i}": f"zeile{i}" for i in range(1, 10)}, "Table of Figures": "zeile1",
                  "Index 1": "zeile1", "Index 2": "zeile2", "Bibliography": "zeile1"}

    def _block_zusatz(self, bfmt: QTextBlockFormat, para: Paragraph) -> None:
        """Verzeichnis- und Beschriftungsabsätze an ihrer Formatvorlage wiedererkennen; Absatzrahmen aus w:pBdr."""
        self._absatzrahmen_lesen(bfmt, para)
        try:
            name = self._ps_name(para)
        except Exception:
            return
        if name in self._TOC_STILE:
            bfmt.setProperty(B_TOC, self._TOC_STILE[name])
            bfmt.setProperty(B_ART, self._toc_art(name, para) or "toc")
        elif name == "Caption":
            erstes = para.text.strip().split(" ")[0] if para.text.strip() else ""
            bfmt.setProperty(B_CAP, erstes if erstes in BESCHRIFTUNGEN else (erstes or "Abbildung"))

    def _absatzrahmen_lesen(self, bfmt: QTextBlockFormat, para: Paragraph) -> None:
        """Absatzrahmen aus w:pBdr: Linie der ersten sichtbaren Seite, alle sichtbaren Seiten, eigener Abstand zum Text."""
        ppr = para._p.pPr
        bdr = ppr.find(qn("w:pBdr")) if ppr is not None else None
        if bdr is None:                                          # nichts am Absatz: Rahmen aus der Formatvorlage (z. B. Linie unter „Titel“)
            bdr = self._style_attr(self._ps(para), lambda s: s.element.find(qn("w:pPr") + "/" + qn("w:pBdr")))
        if bdr is None:
            return
        da = [(kurz, bdr.find(qn(f"w:{x}"))) for x, kurz in _RAHMEN_SEITEN]
        da = [(k, e) for k, e in da if e is not None and e.get(qn("w:val"), "nil") not in ("nil", "none")]
        if da:
            bfmt.setProperty(B_RAHMEN, self._rahmenlinie(da).text())

    @staticmethod
    def _rahmenlinie(da: list) -> Linie:
        """Linie aus der ersten sichtbaren Rahmenseite; Seiten und eigener Abstand (w:space in pt) aus allen."""
        e = da[0][1]
        col = e.get(qn("w:color")) or "000000"
        art = art_aus_docx(e.get(qn("w:val")))
        li = Linie(f"#{col.lower() if col.lower() != 'auto' else '000000'}", int(e.get(qn("w:sz")) or 8) / 8, art).mit_seiten("".join(k for k, _e in da))
        abst = {k: e2.get(qn("w:space")) for k, e2 in da}
        if any(v not in (None, "4") for v in abst.values()):
            li.abstand = ",".join(str(int(abst.get(k) or 4)) for k in "tblr")
        return li

    def _toc_art(self, name: str, para: Paragraph):
        """Art des Verzeichnisses: toc, abb, tab, index, lit — bei Überschriften nach dem folgenden Absatz."""
        if name == "Table of Figures":
            return self._abb_oder_tab(para)
        if name == "TOC Heading":
            return self._toc_art_nach_kopf(para)
        return "toc" if name.startswith("TOC ") else {"Index 1": "index", "Index 2": "index", "Bibliography": "lit"}.get(name)

    @staticmethod
    def _abb_oder_tab(para: Paragraph) -> str:
        return "tab" if para.text.strip().lower().startswith(("tabelle", "table")) else "abb"

    def _toc_art_nach_kopf(self, para: Paragraph) -> str:
        """Verzeichnisüberschrift: die Art ergibt sich aus der Formatvorlage des folgenden Absatzes."""
        nxt = para._p.getnext()
        if nxt is None or nxt.tag != qn("w:p"):
            return "toc"
        folge = Paragraph(nxt, para._parent)
        nn = folge.style.name
        if nn == "Table of Figures" and folge.text.strip().lower().startswith(("tabelle", "table")):
            return "tab"
        return {"Table of Figures": "abb", "Index 1": "index", "Bibliography": "lit"}.get(nn, "toc")

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
