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
from lunivo_writer.services.docx_teile.lesen_metadaten import LesenMetadatenMixin
from lunivo_writer.services.docx_teile.lesen_absatz import LesenAbsatzMixin
from lunivo_writer.services.docx_teile.lesen_runs import LesenRunsMixin



class _Reader(LesenMetadatenMixin, LesenAbsatzMixin, LesenRunsMixin, StilMixin, TabellenMixin, SeiteMixin, ObjekteMixin):
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
