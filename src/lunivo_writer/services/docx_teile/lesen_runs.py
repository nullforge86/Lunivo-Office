"""DOCX lesen: Runs – fachlich gekapselte Verarbeitung."""
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

# Ausrichtung Word → Katalog der Formatvorlagen
_STIL_AUSRICHTUNG = {WD_ALIGN_PARAGRAPH.LEFT: "links", WD_ALIGN_PARAGRAPH.CENTER: "mitte", WD_ALIGN_PARAGRAPH.RIGHT: "rechts",
                     WD_ALIGN_PARAGRAPH.JUSTIFY: "block"}
# Kindelemente eines Laufs → Methode, die sie liest (nicht aufgeführte werden übergangen)
_RUN_ELEMENTE = {
    qn("w:t"): "_run_text", qn("w:delText"): "_run_text", qn("w:tab"): "_run_tab", qn("w:br"): "_run_umbruch", qn("w:cr"): "_run_umbruch",
    qn("w:noBreakHyphen"): "_run_geschuetzter_bindestrich", qn("w:drawing"): "_run_bild", _MC_ALT: "_run_alternativer_inhalt",
    qn("w:footnoteReference"): "_run_notenverweis", qn("w:endnoteReference"): "_run_notenverweis",
}


class LesenRunsMixin:
    """Fachliche Teilverantwortung des DOCX-Readers."""

    def _add_run(self, run, para, cursor: QTextCursor, href: Optional[str] = None) -> bool:
        """→ True, wenn Text oder Bild eingefügt wurde."""
        added = False
        cfmt = self._char_format(run, para)
        self._zusatz_formate(cfmt)
        if href:
            self._link_format(cfmt, href)
        for child in run._r:
            tag = child.tag
            if tag == qn("w:fldChar"):
                neu = self._fldchar_lesen(child, run, para)
                cfmt = neu if neu is not None else cfmt
                continue
            if tag == qn("w:instrText"):
                if self._im_feldcode():
                    self._feld["instr"] += child.text or ""
                continue
            if self._im_feldcode():
                continue
            handler = _RUN_ELEMENTE.get(tag)
            if handler:
                added |= bool(getattr(self, handler)(child, cursor, cfmt))
        return added

    def _im_feldcode(self) -> bool:
        """Steht das Lesen gerade in der Anweisung eines Felds (zwischen begin und separate)?"""
        return bool(self._feld) and self._feld["phase"] == "i"

    def _link_format(self, cfmt: QTextCharFormat, href: str) -> None:
        """Zeichenformat eines Hyperlinks: Ziel, QuickInfo, blaue Unterstreichung."""
        cfmt.setAnchor(True)
        cfmt.setAnchorHref(href)
        if getattr(self, "_link_tipp", ""):
            cfmt.setToolTip(self._link_tipp)
        cfmt.setForeground(QBrush(QColor("#0563C1")))
        cfmt.setFontUnderline(True)

    def _fldchar_lesen(self, child, run, para):
        """Feldzeichen: begin öffnet ein Feld, separate wechselt zum Ergebnis (→ neues Zeichenformat), end schließt es."""
        typ = child.get(qn("w:fldCharType"))
        if typ == "begin":
            self._feld = {"instr": "", "phase": "i"}
        elif typ == "separate" and self._feld:
            self._feld["phase"] = "r"
            cfmt = self._char_format(run, para)
            self._zusatz_formate(cfmt)
            return cfmt
        elif typ == "end":
            self._feld_ende()
        return None

    def _run_text(self, child, cursor, cfmt) -> bool:
        if not child.text:
            return False
        self._flush_break(cursor)
        von = cursor.position()
        cursor.insertText(child.text, cfmt)
        self._letzter = (von, cursor.position())
        self._lz_wartend = []
        return True

    def _run_tab(self, child, cursor, cfmt) -> bool:
        self._flush_break(cursor)
        cursor.insertText("\t", cfmt)
        return True

    def _run_umbruch(self, child, cursor, cfmt) -> bool:
        """Seiten-/Spaltenumbruch wird für den Absatzwechsel vorgemerkt, sonst weicher Zeilenumbruch."""
        if child.get(qn("w:type")) in ("page", "column"):
            self.deferred_break = True
            self.deferred_col = child.get(qn("w:type")) == "column"
        else:
            self._flush_break(cursor)
            cursor.insertText("\u2028", cfmt)
        return False

    def _run_geschuetzter_bindestrich(self, child, cursor, cfmt) -> bool:
        self._flush_break(cursor)
        cursor.insertText("\u2011", cfmt)
        return True

    def _run_bild(self, child, cursor, cfmt) -> bool:
        self._flush_break(cursor)
        self._add_image(child, cursor, cfmt)
        return True

    def _run_alternativer_inhalt(self, child, cursor, cfmt) -> bool:
        """Word legt Formen (Foto im Kreis) in „Alternativer Inhalt“: die Wahl nehmen."""
        added = False
        wahl = child.find(_MC_CHOICE)
        for dr in (wahl.iter(qn("w:drawing")) if wahl is not None else []):
            added |= self._run_bild(dr, cursor, cfmt)
        return added

    def _run_notenverweis(self, child, cursor, cfmt) -> bool:
        """Fuß-/Endnotenverweis als hochgestellte Marke mit Verweis auf die Note."""
        self._flush_break(cursor)
        art = "f" if child.tag == qn("w:footnoteReference") else "e"
        nid = int(child.get(qn("w:id")))
        self._note_n[art] += 1
        nf = QTextCharFormat(cfmt)
        nf.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        nf.setProperty(P_NOTE, f"{art}:{nid}")
        cursor.insertText(self._note_marke(art, self._note_n[art]), nf)
        return True

    @staticmethod
    def _note_marke(art: str, n: int) -> str:
        from lunivo_writer.editor.dokument.zusatz import roemisch
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
        from lunivo_writer.editor.text import stile
        if st.type != WD_STYLE_TYPE.PARAGRAPH or not st.name or "|" in st.name:
            return
        if not stile.ist_eigen(st.name):
            if st.name in stile.VORGABE or len(stile._NEU) >= self.EIGENE_MAX:
                return
            self._vorlage_uebernehmen(st)
        if stile.ist_eigen(st.name):
            b.setProperty(STYLE_PROP, stile.PRAEFIX + st.name)

    def _vorlage_uebernehmen(self, st) -> None:
        """Schrift, Abstände, Ausrichtung und Einzug der Word-Vorlage in den Katalog der Formatvorlagen übernehmen."""
        from lunivo_writer.editor.text import stile
        f, pf = st.font, st.paragraph_format
        stile.anlegen(st.name, groesse=f.size.pt if f.size else 0, fett=bool(f.bold), kursiv=bool(f.italic), farbe=self._vorlagenfarbe(f),
                      schrift=f.name or "", vor=pf.space_before.pt if pf.space_before is not None else 0,
                      nach=pf.space_after.pt if pf.space_after is not None else 0, ausr=_STIL_AUSRICHTUNG.get(pf.alignment, ""),
                      zeilen=float(pf.line_spacing) if isinstance(pf.line_spacing, float) else 0,
                      einzug=round(pf.left_indent.mm, 1) if pf.left_indent is not None else 0)
        self.neue_vorlagen.append(st.name)

    @staticmethod
    def _vorlagenfarbe(f) -> str:
        try:
            return ("#" + str(f.color.rgb)) if f.color is not None and f.color.type is not None and f.color.rgb is not None else ""
        except Exception:
            return ""

    # ---- Hauptlauf ---------------------------------------------------
