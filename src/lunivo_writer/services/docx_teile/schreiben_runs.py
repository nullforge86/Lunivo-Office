"""DOCX schreiben: Runs – fachlich gekapselte Verarbeitung."""
from __future__ import annotations

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

class SchreibenRunsMixin:
    """Fachliche Teilverantwortung des DOCX-Writers."""

    def write_fragment(self, frag, para, in_head: bool):
        cf: QTextCharFormat = frag.charFormat()
        text = frag.text()
        if cf.isImageFormat():
            self._image(cf.toImageFormat(), para)
            return
        parent = getattr(self, "_ziel", None) if getattr(self, "_ziel", None) is not None else para
        href = cf.anchorHref() if cf.isAnchor() else ""
        self._textmarken(para, [] if href else (list(cf.anchorNames()) if cf.isAnchor() else []))
        if href:
            hl = self._hyperlink(para, href, cf.toolTip())
            parent = hl
        note = cf.stringProperty(P_NOTE) if cf.hasProperty(P_NOTE) else ""
        if note:
            run = self._make_run(parent, para)
            self._note_verweis(run, note)
            self._zusatz_anwenden(run, cf)
            return
        for chunk, kind in _split(text):
            run = self._make_run(parent, para)
            if kind == "text":
                run.text = chunk
            elif kind == "tab":
                run.add_tab()
            elif kind == "br":
                run.add_break()
            elif kind == "img":
                continue
            self._format_run(run, cf, in_head, bool(href))
            self._zusatz_anwenden(run, cf)
        if cf.hasProperty(P_INDEX) and cf.stringProperty(P_INDEX):
            from lunivo_writer.editor.indexeintrag import aus_text, feld
            from lunivo_writer.editor.zusatz import P_INDEX_OPT
            self._fldchar(para, "begin")
            self._instr(para, feld(aus_text(cf.stringProperty(P_INDEX), cf.stringProperty(P_INDEX_OPT) if cf.hasProperty(P_INDEX_OPT) else "")))
            self._fldchar(para, "end")

    def _textmarken(self, para, namen: list) -> None:
        """Offene Textmarken schließen, neue öffnen — je Name genau ein bookmarkStart/-End-Paar."""
        for n in [n for n in self._lz_offen if n not in namen]:
            e = OxmlElement("w:bookmarkEnd")
            e.set(qn("w:id"), str(self._lz_offen.pop(n)))
            para._p.append(e)
        for n in namen:
            if n not in self._lz_offen:
                self._lz_id += 1
                st = OxmlElement("w:bookmarkStart")
                st.set(qn("w:id"), str(self._lz_id)); st.set(qn("w:name"), n)
                para._p.append(st)
                self._lz_offen[n] = self._lz_id

    def _note_verweis(self, run, note: str) -> None:
        art, _, nid = note.partition(":")
        nid = int(nid)
        key = (art, nid)
        if key not in self._note_ids:
            self._note_ids[key] = len(self._noten[art]) + 1
            self._noten[art].append((self._note_ids[key], (self.meta.get("noten", {}).get(art, {}) or {}).get(nid, "")))
        r = run._r
        for k in list(r):
            r.remove(k)
        rpr = OxmlElement("w:rPr")
        rs = OxmlElement("w:rStyle"); rs.set(qn("w:val"), "FootnoteReference" if art == "f" else "EndnoteReference")
        rpr.append(rs)
        r.append(rpr)
        ref = OxmlElement("w:footnoteReference" if art == "f" else "w:endnoteReference")
        ref.set(qn("w:id"), str(self._note_ids[key]))
        r.append(ref)

    def _zusatz_anwenden(self, run, cf: QTextCharFormat) -> None:
        """Kommentarbereich merken, nachverfolgte Änderung als w:ins / w:del um den Lauf legen."""
        if cf.hasProperty(P_KOMMENTAR):
            self._komm_runs.setdefault(int(cf.property(P_KOMMENTAR)), []).append(run)
        if cf.hasProperty(P_AENDERUNG):
            art = cf.stringProperty(P_AENDERUNG)
            if art in ("ins", "del"):
                self._aend_id += 1
                w = OxmlElement("w:ins" if art == "ins" else "w:del")
                w.set(qn("w:id"), str(1000 + self._aend_id))
                w.set(qn("w:author"), cf.stringProperty(P_AUTOR) or "Unbekannt")
                if cf.stringProperty(P_DATUM):
                    w.set(qn("w:date"), cf.stringProperty(P_DATUM))
                run._r.addprevious(w)
                w.append(run._r)
                if art == "del":
                    for t in run._r.findall(qn("w:t")):
                        t.tag = qn("w:delText")

    def _steuerelement(self, form: str, wert: str):
        """w:sdt für ein Formularfeld: Art (Text, Liste, Datum, Kontrollkästchen), Name als Titel, unsere Daten im Tag."""
        from lunivo_writer.editor import formular as FO
        m = FO.meta_lesen(form) or {"art": "text", "name": ""}
        W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
        sdt = OxmlElement("w:sdt")
        pr = OxmlElement("w:sdtPr")
        sdt.append(pr)
        if m.get("name"):
            al = OxmlElement("w:alias"); al.set(qn("w:val"), str(m["name"])); pr.append(al)
        tag = OxmlElement("w:tag"); tag.set(qn("w:val"), "lunivo:" + form); pr.append(tag)
        if m.get("leer"):
            pr.append(OxmlElement("w:showingPlcHdr"))
        art = m["art"]
        if art == "text":
            pr.append(OxmlElement("w:text"))
        elif art == "auswahl":
            dd = OxmlElement("w:dropDownList")
            for o in m.get("optionen") or []:
                li = OxmlElement("w:listItem"); li.set(qn("w:displayText"), str(o)); li.set(qn("w:value"), str(o)); dd.append(li)
            pr.append(dd)
        elif art == "datum":
            da = OxmlElement("w:date")
            fm = OxmlElement("w:dateFormat"); fm.set(qn("w:val"), FO.DATUMSFORMAT); da.append(fm)
            lid = OxmlElement("w:lid"); lid.set(qn("w:val"), "de-DE"); da.append(lid)
            pr.append(da)
        elif art == "kasten":
            from lxml import etree
            cb = etree.SubElement(pr, "{%s}checkbox" % W14)
            for nm, val in (("checked", "1" if wert.strip() == FO.KASTEN_VOLL else "0"), ("checkedState", "2612"), ("uncheckedState", "2610")):
                el = etree.SubElement(cb, "{%s}%s" % (W14, nm)); el.set("{%s}val" % W14, val)
        inhalt = OxmlElement("w:sdtContent")
        sdt.append(inhalt)
        return sdt, inhalt

    def _make_run(self, parent, para):
        if parent is para:
            return para.add_run()
        from docx.text.run import Run
        r = OxmlElement("w:r")
        parent.append(r)
        return Run(r, para)

    def _hyperlink(self, para, href: str, tipp: str = ""):
        h = OxmlElement("w:hyperlink")
        if tipp:
            h.set(qn("w:tooltip"), tipp)                        # QuickInfo aus dem Fenster „Hyperlink“
        if href.startswith("#"):
            h.set(qn("w:anchor"), href[1:])
        else:
            rid = para.part.relate_to(href, RT.HYPERLINK, is_external=True)
            h.set(qn("r:id"), rid)
        para._p.append(h)
        return h

    def _format_run(self, run, cf: QTextCharFormat, in_head: bool, is_link: bool):
        f = run.font
        if _has(cf, QTextFormat.FontFamilies) and cf.fontFamilies():
            fam = cf.fontFamilies()[0]
            f.name = fam
            rpr = run._r.get_or_add_rPr()
            rf = rpr.find(qn("w:rFonts"))
            for a in ("w:hAnsi", "w:cs", "w:eastAsia"):
                rf.set(qn(a), fam)
            from lunivo_writer.editor.zusatz import P_FONT_ASIEN, P_FONT_KOMPLEX
            for prop, attr in ((P_FONT_ASIEN, "w:eastAsia"), (P_FONT_KOMPLEX, "w:cs")):      # Schrift für asiatische und komplexe Zeichen
                if cf.hasProperty(prop) and cf.stringProperty(prop).split("|")[0]:
                    rf.set(qn(attr), cf.stringProperty(prop).split("|")[0])
        elif _has(cf, QTextFormat.FontFamily):
            f.name = cf.stringProperty(QTextFormat.FontFamily)
        if _has(cf, QTextFormat.FontPointSize) and cf.fontPointSize() > 0:
            f.size = Pt(cf.fontPointSize())
        if _has(cf, QTextFormat.FontWeight):
            f.bold = cf.fontWeight() >= QFont.DemiBold
        if _has(cf, QTextFormat.FontItalic):
            f.italic = cf.fontItalic()
        ustil = cf.underlineStyle()
        from lunivo_writer.editor.zusatz import P_UNTER
        eigene = cf.stringProperty(P_UNTER) if cf.hasProperty(P_UNTER) else ""
        if (ustil != QTextCharFormat.NoUnderline or eigene) and not is_link:
            from docx.enum.text import WD_UNDERLINE as U
            f.underline = {"woerter": U.WORDS, "doppelt": U.DOUBLE, "dick": U.THICK, "dick_gepunktet": U.DOTTED_HEAVY, "dick_gestrichelt": U.DASH_HEAVY,
                           "lang": U.DASH_LONG, "dick_lang": U.DASH_LONG_HEAVY, "dick_strichpunkt": U.DOT_DASH_HEAVY, "dick_strichpunktpunkt": U.DOT_DOT_DASH_HEAVY,
                           "dick_wellig": U.WAVY_HEAVY, "doppelwellig": U.WAVY_DOUBLE}.get(eigene) or {
                QTextCharFormat.DashUnderline: U.DASH, QTextCharFormat.DotLine: U.DOTTED, QTextCharFormat.DashDotLine: U.DOT_DASH,
                QTextCharFormat.DashDotDotLine: U.DOT_DOT_DASH, QTextCharFormat.WaveUnderline: U.WAVY}.get(ustil, True)
        from lunivo_writer.editor.zusatz import P_BETONUNG, P_DOPPELT, P_FONT_KOMPLEX
        if cf.hasProperty(P_DOPPELT) and cf.property(P_DOPPELT):
            f.double_strike = True
        elif cf.fontStrikeOut():
            f.strike = True
        if cf.hasProperty(P_FONT_KOMPLEX):                       # Schnitt und Größe für komplexe Zeichen
            _fam, schnitt, gr = (cf.stringProperty(P_FONT_KOMPLEX).split("|") + ["", "", ""])[:3]
            f.cs_bold = True if "Fett" in schnitt else None
            f.cs_italic = True if "Kursiv" in schnitt else None
            try:
                if float(gr or 0) > 0:
                    sz = OxmlElement("w:szCs"); sz.set(qn("w:val"), str(int(round(float(gr) * 2))))
                    _rpr_einfuegen(run._r.get_or_add_rPr(), sz)
            except ValueError:
                pass
        from lunivo_writer.editor.zusatz import P_RASTER
        rpr_ = run._r.get_or_add_rPr()
        if cf.hasProperty(QTextFormat.FontStretch) and cf.fontStretch() not in (0, 100):               # Skalieren
            e_ = OxmlElement("w:w"); e_.set(qn("w:val"), str(int(cf.fontStretch()))); _rpr_einfuegen(rpr_, e_)
        if cf.hasProperty(QTextFormat.TextBaselineOffset) and cf.baselineOffset() and cf.verticalAlignment() == QTextCharFormat.AlignNormal:  # Position
            gr = cf.fontPointSize() if cf.hasProperty(QTextFormat.FontPointSize) and cf.fontPointSize() > 0 else 11.0
            e_ = OxmlElement("w:position"); e_.set(qn("w:val"), str(int(round(cf.baselineOffset() * gr / 100 * 2)))); _rpr_einfuegen(rpr_, e_)
        if cf.hasProperty(P_RASTER) and not cf.property(P_RASTER):
            e_ = OxmlElement("w:snapToGrid"); e_.set(qn("w:val"), "0"); _rpr_einfuegen(rpr_, e_)
        if cf.hasProperty(P_BETONUNG) and cf.stringProperty(P_BETONUNG):
            em = OxmlElement("w:em")
            em.set(qn("w:val"), {"punkt": "dot", "kreis": "circle", "komma": "comma", "unten": "underDot"}.get(cf.stringProperty(P_BETONUNG), "dot"))
            _rpr_einfuegen(run._r.get_or_add_rPr(), em)
        va = cf.verticalAlignment()
        if va == QTextCharFormat.AlignSuperScript:
            f.superscript = True
        elif va == QTextCharFormat.AlignSubScript:
            f.subscript = True
        fg = cf.foreground()
        if fg.style() != Qt.NoBrush and not is_link:
            c = fg.color()
            if c.isValid() and c.name().lower() != Farbe.SCHWARZ:
                f.color.rgb = RGBColor(c.red(), c.green(), c.blue())
        bg = cf.background()
        if bg.style() != Qt.NoBrush:
            c = bg.color()
            if c.isValid():
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:color"), "auto")
                shd.set(qn("w:fill"), c.name()[1:].upper())
                run._r.get_or_add_rPr().append(shd)
        if cf.textOutline().style() != Qt.NoPen:
            f.outline = True
        from lunivo_writer.editor.zusatz import P_EFFEKT
        if cf.textOutline().style() != Qt.NoPen or cf.stringProperty(P_EFFEKT) or (cf.hasProperty(QTextFormat.ForegroundBrush) and cf.foreground().color().alpha() < 255):
            from lunivo_writer.editor import texteffekt
            texteffekt.in_rpr(run._r.get_or_add_rPr(), cf)
        if cf.hasProperty(P_VERSTECKT):
            f.hidden = True
        ls = cf.fontLetterSpacing()
        if ls and cf.fontLetterSpacingType() == QFont.AbsoluteSpacing:
            sp = OxmlElement("w:spacing")
            sp.set(qn("w:val"), str(int(round(ls * 0.75 * 20))))             # px → pt → Zwanzigstelpunkt
            run._r.get_or_add_rPr().insert_element_before(
                sp, "w:w", "w:kern", "w:position", "w:sz", "w:szCs", "w:highlight", "w:u", "w:effect", "w:bdr", "w:shd",
                "w:fitText", "w:vertAlign", "w:rtl", "w:cs", "w:em", "w:lang", "w:eastAsianLayout", "w:specVanish", "w:oMath")
        cap = cf.fontCapitalization()
        if cap == QFont.AllUppercase:
            f.all_caps = True
        elif cap == QFont.SmallCaps:
            f.small_caps = True
        if is_link:
            run._r.get_or_add_rPr().append(_rstyle_hyperlink(self.d))

    # Kompatibilitätsoptionen (Optionen ▸ Allgemein und Speichern): als echte Einstellungen in settings.xml; Reihenfolge nach ECMA-376
    KOMPAT_VOR_FE = ("ulTrailSpace", "footnoteLayoutLikeWW8", "adjustLineHeightInTable")
    KOMPAT_NACH_FE = ("doNotUseIndentAsNumberingTabStop", "splitPgBreakAndParaMark")
