"""DOCX → QTextDocument (python-docx).

Gelesen werden: Absätze mit Formatvorlage, Überschriften, Zeichenformat
(Schrift, Größe, Fett, Kursiv, Unterstrichen, Durchgestrichen, Hoch/Tief,
Farbe, Hervorhebung), Ausrichtung, Einzüge, Abstände, Zeilenabstand,
Aufzählungen und Nummerierungen, Seitenumbrüche, Tabellen (mit verbundenen
Zellen), Bilder im Text, Hyperlinks, Seitengröße, Ränder, Kopf- und Fußzeile.

Alles, was nicht gelesen wird, landet im IOReport — nichts verschwindet still.
"""
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
from lunivo_writer.services.docx_teile.lesen_stile import StilMixin
from lunivo_writer.services.docx_teile.lesen_tabellen import TabellenMixin
from lunivo_writer.services.docx_teile.lesen_seite import SeiteMixin
from lunivo_writer.services.docx_teile.lesen_objekte import ObjekteMixin


class _Reader(StilMixin, TabellenMixin, SeiteMixin, ObjekteMixin):
    def __init__(self, path: str):
        self.path = path
        self.report = IOReport()
        try:
            self.d = docx.Document(path)
        except (zipfile.BadZipFile, KeyError, ValueError) as e:
            raise DocumentIOError(
                "Die Datei ist kein gültiges DOCX-Dokument oder beschädigt.") from e
        except Exception as e:  # python-docx wirft viele Typen bei kaputten Paketen
            from lunivo_writer.plattform import protokoll
            protokoll.unerwartet(logging.getLogger("lunivo.dateien"), "DOCX lesen", e)
            raise DocumentIOError(f"Die Datei konnte nicht gelesen werden: {e}") from e
        self.doc = QTextDocument()
        self.doc.setDocumentMargin(0)
        self.cur = QTextCursor(self.doc)
        self.fresh = True                 # aktueller Block ist leer und noch frei
        self.last_list = None             # (key, QTextList)
        self.pending_break = False
        self._ab_zaehler = 0
        self.neue_vorlagen: list[str] = []
        self._erste_seite = None
        self.deferred_break = False       # Seitenumbruch im Absatz, danach folgt noch nichts
        self.img_n = 0
        self.zus = leere_meta()
        self._komm_offen: list[int] = []
        self._lz_offen: dict[str, str] = {}
        self._lz_pos: dict[str, int] = {}
        self._lz_wartend: list[str] = []
        self._aend = None                 # (art, autor, datum) innerhalb w:ins / w:del
        self._form = None                 # JSON-Text des Formularfelds innerhalb w:sdt
        self._note_n = {"f": 0, "e": 0}
        self._feld = None                 # {"instr", "phase": "i"|"r"} innerhalb eines Feldes
        self._letzter = None              # (von, bis) des zuletzt eingefügten Textstücks (für XE-Felder)
        self._laden_zusatz()
        self._stile_id = {st.style_id: st for st in self.d.styles}          # Zwischenspeicher: python-docx sucht sonst bei jedem Zugriff per XPath
        self._standard_absatz = self._standard_stil(WD_STYLE_TYPE.PARAGRAPH)
        self._standard_zeichen = self._standard_stil(WD_STYLE_TYPE.CHARACTER)
        self._basis: dict[int, object] = {}
        self._ketten: dict[int, list] = {}
        self._attr_cache: dict[tuple, object] = {}
        self.def_font, self.def_size = _doc_defaults(self.d)
        normal = self.d.styles["Normal"] if "Normal" in [s.name for s in self.d.styles] else None
        self.normal = normal

    def _laden_zusatz(self) -> None:
        """Kommentare (python-docx) und Fuß-/Endnoten (Teile footnotes.xml / endnotes.xml) einlesen."""
        try:
            for c in self.d.comments:
                self.zus["kommentare"][int(c.comment_id)] = {
                    "autor": c.author or "", "initialen": c.initials or "",
                    "datum": c.timestamp.isoformat() if c.timestamp else "",
                    "text": "\n".join(p.text for p in c.paragraphs)}
        except Exception:
            self.report.warn("Kommentare konnten nicht gelesen werden.")
        self._kommentare_geloest_lesen()
        self._quellen_lesen()
        for art, rel in (("f", "footnotes"), ("e", "endnotes")):
            for r in self.d.part.rels.values():
                if r.reltype.endswith("/" + rel) and not r.is_external:
                    from lxml import etree
                    wurzel = etree.fromstring(r.target_part.blob, lxml_parser())
                    tag = qn("w:footnote") if art == "f" else qn("w:endnote")
                    for n in wurzel.iterchildren(tag):
                        if n.get(qn("w:type")) in ("separator", "continuationSeparator", "continuationNotice"):
                            continue
                        zeilen = []
                        for p in n.iterchildren(qn("w:p")):
                            zeilen.append("".join(t.text or "" for t in p.iter(qn("w:t"))).strip())
                        self.zus["noten"][art][int(n.get(qn("w:id")))] = "\n".join(zeilen)

    def _kommentare_geloest_lesen(self) -> None:
        """Welche Kommentare Word als gelöst markiert hat (Teil commentsExtended: w15:done je Absatzkennung)."""
        try:
            from lxml import etree
            W14 = "{http://schemas.microsoft.com/office/word/2010/wordml}paraId"
            W15 = "{http://schemas.microsoft.com/office/word/2012/wordml}"
            fertig = set()
            for r in self.d.part.rels.values():
                if r.reltype.endswith("/commentsExtended") and not r.is_external:
                    for e in etree.fromstring(r.target_part.blob, lxml_parser()).iter(W15 + "commentEx"):
                        if e.get(W15 + "done") in ("1", "true"):
                            fertig.add(e.get(W15 + "paraId"))
            if not fertig:
                return
            for c in self.d.comments:
                ps = c.paragraphs
                if ps and ps[0]._p.get(W14) in fertig and int(c.comment_id) in self.zus["kommentare"]:
                    self.zus["kommentare"][int(c.comment_id)]["geloest"] = True
        except Exception:                                              # noqa: BLE001 — ein unlesbarer Zusatzteil darf das Laden nicht verhindern
            pass

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
                self.zus["quellen"].append({"tag": t("Tag"), "typ": typ, "autor": "; ".join(personen), "titel": t("Title"),
                                            "jahr": t("Year"), "verlag": t("Publisher"), "ort": t("City"), "url": t("URL")})


    _HL = {"yellow": "#FFFF00", "green": "#00FF00", "cyan": "#00FFFF", "magenta": "#FF00FF",
           "blue": "#0000FF", "red": "#FF0000", "darkBlue": "#000080", "darkCyan": "#008080",
           "darkGreen": "#008000", "darkMagenta": "#800080", "darkRed": "#800000",
           "darkYellow": "#808000", "darkGray": "#808080", "lightGray": "#C0C0C0",
           "black": Farbe.SCHWARZ}


    # ---- Absatzformat ------------------------------------------------
    _JC = {"left": Qt.AlignLeft, "start": Qt.AlignLeft, "right": Qt.AlignRight, "end": Qt.AlignRight, "center": Qt.AlignHCenter,
           "both": Qt.AlignJustify, "distribute": Qt.AlignJustify, "justify": Qt.AlignJustify}


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

    def _add_run(self, run, para, cursor: QTextCursor, href: Optional[str] = None) -> bool:
        """→ True, wenn Text oder Bild eingefügt wurde."""
        added = False
        cfmt = self._char_format(run, para)
        self._zusatz_formate(cfmt)
        if href:
            cfmt.setAnchor(True)
            cfmt.setAnchorHref(href)
            if getattr(self, "_link_tipp", ""):
                cfmt.setToolTip(self._link_tipp)
            cfmt.setForeground(QBrush(QColor("#0563C1")))
            cfmt.setFontUnderline(True)
        for child in run._r:
            tag = child.tag
            if tag == qn("w:fldChar"):
                typ = child.get(qn("w:fldCharType"))
                if typ == "begin":
                    self._feld = {"instr": "", "phase": "i"}
                elif typ == "separate" and self._feld:
                    self._feld["phase"] = "r"
                    cfmt = self._char_format(run, para)
                    self._zusatz_formate(cfmt)
                elif typ == "end":
                    self._feld_ende()
                continue
            if tag == qn("w:instrText"):
                if self._feld and self._feld["phase"] == "i":
                    self._feld["instr"] += child.text or ""
                continue
            if self._feld and self._feld["phase"] == "i":
                continue
            if tag == qn("w:t") or tag == qn("w:delText"):
                if child.text:
                    self._flush_break(cursor)
                    von = cursor.position()
                    cursor.insertText(child.text, cfmt)
                    self._letzter = (von, cursor.position())
                    self._lz_wartend = []
                    added = True
            elif tag == qn("w:tab"):
                self._flush_break(cursor)
                cursor.insertText("\t", cfmt)
                added = True
            elif tag in (qn("w:br"), qn("w:cr")):
                if child.get(qn("w:type")) in ("page", "column"):
                    self.deferred_break = True
                    self.deferred_col = child.get(qn("w:type")) == "column"
                else:
                    self._flush_break(cursor)
                    cursor.insertText("\u2028", cfmt)
            elif tag == qn("w:noBreakHyphen"):
                self._flush_break(cursor)
                cursor.insertText("\u2011", cfmt)
                added = True
            elif tag == qn("w:drawing"):
                self._flush_break(cursor)
                self._add_image(child, cursor, cfmt)
                added = True
            elif tag == _MC_ALT:                                      # Word legt Formen (Foto im Kreis) in „Alternativer Inhalt“: die Wahl nehmen
                wahl = child.find(_MC_CHOICE)
                for dr in (wahl.iter(qn("w:drawing")) if wahl is not None else []):
                    self._flush_break(cursor)
                    self._add_image(dr, cursor, cfmt)
                    added = True
            elif tag in (qn("w:footnoteReference"), qn("w:endnoteReference")):
                self._flush_break(cursor)
                art = "f" if tag == qn("w:footnoteReference") else "e"
                nid = int(child.get(qn("w:id")))
                self._note_n[art] += 1
                nf = QTextCharFormat(cfmt)
                nf.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
                nf.setProperty(P_NOTE, f"{art}:{nid}")
                cursor.insertText(self._note_marke(art, self._note_n[art]), nf)
                added = True
        return added

    @staticmethod
    def _note_marke(art: str, n: int) -> str:
        from lunivo_writer.editor.zusatz import roemisch
        return str(n) if art == "f" else roemisch(n)


    def _umbruch_seite(self, drawing, breite_px: float) -> str:
        """„links“/„rechts“, wenn das Bild den Text umfließt (wrapSquare/Tight/Through); sonst leer."""
        anker = drawing.xpath("wp:anchor")
        if not anker or not _xp(anker[0], "wp:wrapSquare | wp:wrapTight | wp:wrapThrough"):
            return ""
        h = _xp(anker[0], "wp:positionH")
        if h:
            al = _xp(h[0], "wp:align/text()")
            if al:
                return "rechts" if al[0] in ("right", "outside") else "links"
            off = _xp(h[0], "wp:posOffset/text()")
            if off:
                try:
                    sec = self.d.sections[0]
                    inhalt = _emu_to_px(sec.page_width - sec.left_margin - sec.right_margin)
                except Exception:                                                      # noqa: BLE001
                    inhalt = 600.0
                return "rechts" if _emu_to_px(off[0]) + breite_px / 2 > inhalt / 2 else "links"
        return "links"

    EIGENE_MAX = 20                                                  # so viele Vorlagen nimmt ein Dokument höchstens in den Katalog auf

    def _eigene_vorlage(self, st, b) -> None:
        """Eine selbst angelegte Absatzvorlage des Dokuments: der Absatz behält ihren Namen; fehlt sie im Katalog, wird sie übernommen."""
        from docx.enum.style import WD_STYLE_TYPE
        from lunivo_writer.editor import stile
        if st.type != WD_STYLE_TYPE.PARAGRAPH or not st.name or "|" in st.name:
            return
        if not stile.ist_eigen(st.name):
            if st.name in stile.VORGABE or len(stile._NEU) >= self.EIGENE_MAX:
                return
            f, pf = st.font, st.paragraph_format
            try:
                farbe = ("#" + str(f.color.rgb)) if f.color is not None and f.color.type is not None and f.color.rgb is not None else ""
            except Exception:
                farbe = ""
            ausr = {WD_ALIGN_PARAGRAPH.LEFT: "links", WD_ALIGN_PARAGRAPH.CENTER: "mitte", WD_ALIGN_PARAGRAPH.RIGHT: "rechts",
                    WD_ALIGN_PARAGRAPH.JUSTIFY: "block"}.get(pf.alignment, "")
            stile.anlegen(st.name, groesse=f.size.pt if f.size else 0, fett=bool(f.bold), kursiv=bool(f.italic), farbe=farbe,
                          schrift=f.name or "", vor=pf.space_before.pt if pf.space_before is not None else 0,
                          nach=pf.space_after.pt if pf.space_after is not None else 0, ausr=ausr,
                          zeilen=float(pf.line_spacing) if isinstance(pf.line_spacing, float) else 0,
                          einzug=round(pf.left_indent.mm, 1) if pf.left_indent is not None else 0)
            self.neue_vorlagen.append(st.name)
        if stile.ist_eigen(st.name):
            b.setProperty(STYLE_PROP, stile.PRAEFIX + st.name)


    # ---- Hauptlauf ---------------------------------------------------
    def run(self):
        body = self.d.element.body
        for pat, msg in _UNSUPPORTED:
            try:
                if _xp(body, pat):
                    self.report.warn(msg)
            except Exception:
                pass
        def kinder(eltern):
            for c in eltern.iterchildren():
                if c.tag == qn("w:sdt"):
                    inhalt = c.find(qn("w:sdtContent"))
                    if inhalt is not None:
                        yield from kinder(inhalt)
                else:
                    yield c
        self._erste_seite = self.read_page()
        for child in kinder(body):
            if child.tag == qn("w:p"):
                self.fresh = self.add_paragraph(Paragraph(child, self.d._body), self.cur, reuse=self.fresh)
            elif child.tag == qn("w:tbl"):
                self.add_table(Table(child, self.d._body))
        self._ketten_bereinigen()
        # leeren Schlussblock nach Tabelle behalten (Qt braucht ihn)
        page = self._erste_seite
        df = QFont(self.def_font or "Calibri")
        df.setPointSizeF(self.def_size or 11.0)
        self.doc.setDefaultFont(df)
        props = self.d.core_properties
        meta = {"title": props.title or "", "author": props.author or ""}
        meta.update(self.zus)
        lang = self.d.styles.element.find(qn("w:docDefaults") + "/" + qn("w:rPrDefault") + "/" + qn("w:rPr") + "/" + qn("w:lang"))
        if lang is not None and lang.get(qn("w:val")):
            meta["sprache"] = lang.get(qn("w:val"))
        self.doc.setModified(False)
        return self.doc, page, meta, self.report


def _schriften_ersatz() -> None:
    """Word-Schriften ohne Entsprechung im System ersetzt Qt sonst durch irgendeine breite Schrift (so wurde aus „Calibri Light“ Noto Sans).
    Die metrikgleichen Schriften (Carlito, Caladea) halten Zeilenhöhe und Umbruch gleich."""
    from PySide6.QtGui import QFont, QFontDatabase
    vorhanden = set(QFontDatabase.families())
    for name, ersatz in _ERSATZ.items():
        wahl = [e for e in ersatz if e in vorhanden]
        if wahl and name not in vorhanden:
            QFont.insertSubstitutions(name, wahl)


def read_docx(path: str):
    """→ (QTextDocument, PageSettings, meta-dict, IOReport). Wirft DocumentIOError."""
    from lunivo_writer.services.import_grenzen import pruefe_paket
    pruefe_paket(path, "DOCX")                       # Grenzen zuerst, bevor irgendetwas gelesen wird
    _schriften_ersatz()
    return _Reader(path).run()
