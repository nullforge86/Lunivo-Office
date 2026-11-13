"""QTextDocument → DOCX (python-docx).

Schreibt Absätze, Überschriften (Formatvorlagen „Heading n“), Titel/Untertitel/
Zitat, Zeichenformat, Ausrichtung, Einzüge, Abstände, Zeilenabstand, Listen,
Seitenumbrüche, Tabellen (mit verbundenen Zellen), Bilder, Hyperlinks,
Seitengröße, Ränder, Kopf- und Fußzeile (mit Seitenzahlfeld).
"""
from __future__ import annotations

from dataclasses import fields
from math import isfinite

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
from lunivo_writer.dienste.docx_teile.schreiben_seite import SeiteSchreiber
from lunivo_writer.dienste.docx_teile.schreiben_tabellen import TabellenSchreiber
from lunivo_writer.dienste.docx_teile.schreiben_objekte import ObjekteSchreiber
from lunivo_writer.dienste.docx_teile.schreiben_textfelder import TextfeldSchreiber
from lunivo_writer.dienste.docx_teile.schreiben_zusatz import ZusatzSchreiber
from lunivo_writer.dienste.docx_teile.schreiben_dokument import SchreibenDokumentMixin
from lunivo_writer.dienste.docx_teile.schreiben_absatz import SchreibenAbsatzMixin
from lunivo_writer.dienste.docx_teile.schreiben_runs import SchreibenRunsMixin



class _Writer(SchreibenDokumentMixin, SchreibenAbsatzMixin, SchreibenRunsMixin, SeiteSchreiber, TabellenSchreiber, ObjekteSchreiber, TextfeldSchreiber, ZusatzSchreiber):
    def __init__(self, qdoc: QTextDocument, page: PageSettings, meta: dict):
        self.q = qdoc
        self.page = page
        self.meta = meta
        self.report = IOReport()
        self.d = docx.Document()
        self._clear_body()
        self._num_ids: dict[tuple, int] = {}
        self._vorab_bilder: list = []                    # schwebende Bilder, die am nächsten Absatz verankert werden
        self.last_list_obj = None
        self.last_num = None
        self._komm_runs: dict[int, list] = {}
        self._noten: dict[str, list] = {"f": [], "e": []}       # [(Ausgabe-Id, Text)]
        self._note_ids: dict[tuple, int] = {}
        self._aend_id = 0
        self._lz_id = 0
        self._lz_offen: dict[str, int] = {}























    def _kompatibilitaet(self) -> None:
        gewaehlt = set(self.meta.get("kompat") or [])
        einst = self.d.settings.element
        if "bilder_komprimieren" in self.meta:
            wort = einst.find(qn("w:doNotAutoCompressPictures"))
            if self.meta["bilder_komprimieren"] and wort is not None:
                einst.remove(wort)                                    # Textprogramme dürfen Bilder beim Speichern selbst komprimieren
        if not gewaehlt:
            return
        compat = einst.find(qn("w:compat"))
        if compat is None:
            return
        for name in self.KOMPAT_VOR_FE[::-1]:
            if name in gewaehlt and compat.find(qn(f"w:{name}")) is None:
                compat.insert(0, OxmlElement(f"w:{name}"))
        fe = compat.find(qn("w:useFELayout"))
        stelle = list(compat).index(fe) + 1 if fe is not None else 0
        for name in self.KOMPAT_NACH_FE:
            if name in gewaehlt and compat.find(qn(f"w:{name}")) is None:
                compat.insert(stelle, OxmlElement(f"w:{name}"))
                stelle += 1


    _WPS = "http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
    _MC = "http://schemas.openxmlformats.org/markup-compatibility/2006"


    _RAND_VAL = {QTextFrameFormat.BorderStyle_Dotted: "dotted", QTextFrameFormat.BorderStyle_Dashed: "dashed",
                 QTextFrameFormat.BorderStyle_Double: "double"}


    # ---- Hauptlauf --------------------------------------------------------
    def run(self) -> bytes:
        self.write_defaults()
        self._sprache()
        self.write_page()
        self.write_frame(self.q.rootFrame(), _Body(self.d))
        self._trim_trailing_empty()
        self._noten_schreiben()
        self._kommentare_schreiben()
        self._quellen_schreiben()
        self._kompatibilitaet()
        cp = self.d.core_properties
        cp.title = self.meta.get("title", "") or ""
        cp.author = self.meta.get("author", "") or "Lunivo Writer"
        out = io.BytesIO()
        self.d.save(out)
        return out.getvalue()


    def _trim_trailing_empty(self):
        body = self.d.element.body
        kids = [k for k in body if k.tag != qn("w:sectPr")]
        # Textprogramme verlangen nach einer Tabelle einen Absatz; leere Endabsätze sonst entfernen
        while len(kids) > 1 and kids[-1].tag == qn("w:p") and not "".join(kids[-1].itertext()).strip() \
                and kids[-2].tag == qn("w:p") and not kids[-1].xpath(".//w:drawing"):
            body.remove(kids[-1])
            kids.pop()


def docx_daten(qdoc: QTextDocument, page: PageSettings, meta: Optional[dict] = None) -> tuple[bytes, IOReport]:
    """Baut die DOCX-Datei im Speicher. → (Inhalt, Bericht). Wirft DocumentIOError."""
    w = _Writer(qdoc, page, meta or {})
    try:
        data = w.run()
    except Exception as e:
        logging.getLogger("lunivo.dateien").exception("DOCX konnte nicht aufgebaut werden")
        raise DocumentIOError(f"Das Dokument konnte nicht als DOCX aufgebaut werden: {e}") from e
    return data, w.report


def docx_modell_daten(modell, page: PageSettings, meta: Optional[dict] = None) -> tuple[bytes, IOReport] | None:
    """Schreibt einfache Modellabsätze, eingebettete Bilder und Tabellen direkt als DOCX; ``None`` bedeutet: Modell über den Qt-Schreiber sichern.

    Der Umfang ist absichtlich eng: ein Abschnitt, einfache Zeichen- und Absatzformate sowie Tabellen ohne feste Spaltenvorgaben und ohne verschachtelte
    Blöcke. Tabellenrahmen, Innen- und Außenabstände, wiederholte Kopfzeilen, Zeilenhöhen, vertikale Zellenausrichtung und deckende Vollton-Zellfüllungen werden übernommen. Jede nicht abgebildete Eigenschaft führt zum Rückfall, damit der Modellweg keine Daten stillschweigend auslässt.
    """
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_ROW_HEIGHT_RULE
    from docx.shared import Mm, Pt, RGBColor
    from lunivo_writer.core.document import Document as CoreDocument, Image as ModelImage, Paragraph, Table, TextRun
    from lunivo_writer.core.document.values import Brush, Color, Length
    from lunivo_writer.modelle.seite import PageSettings as PageSettingsType

    m = meta or {}
    if not isinstance(modell, CoreDocument) or len(modell.sections) != 1 or modell.notes or modell.lists or modell.media:
        return None
    root_standard = {"FrameMargin": 4.0, "FrameTopMargin": 4.0, "FrameBottomMargin": 4.0, "FrameLeftMargin": 4.0,
                     "FrameRightMargin": 4.0, "FrameBorderBrush": Brush(1, Color(128, 128, 128)), "FrameBorderStyle": 10}
    text_standard = {"tab_stop_distance": 80.0, "wrap_mode": 4, "alignment": 1, "direction": 2, "flags": 0,
                     "design_metrics": False, "tabs": ()}
    if modell.root_properties not in ({}, root_standard) or modell.text_option not in ({}, text_standard) \
            or modell.document_margin not in (0, 4.0) or modell.indent_width != 40:
        return None
    if any(k not in {"title", "author", "sprache", "kennwort", "bilder_komprimieren", "kompat"} for k in m) \
            or m.get("bilder_komprimieren") or m.get("kompat"):
        return None
    section = modell.sections[0]
    if section.kind != "naechste" or (section.page is not None and section.page != page):
        return None
    if not isinstance(page, PageSettingsType):
        return None
    standard = PageSettingsType()
    seiten_ausnahme = {"width_mm", "height_mm", "margin_top_mm", "margin_bottom_mm", "margin_left_mm", "margin_right_mm"}
    if any(getattr(page, f.name) != getattr(standard, f.name) for f in fields(page) if f.name not in seiten_ausnahme):
        return None

    zeichen_schluessel = {"FontFamilies", "FontFamily", "FontPointSize", "FontWeight", "FontItalic", "FontUnderline", "TextUnderlineStyle", "ForegroundBrush"}
    absatz_schluessel = {"BlockAlignment", "BlockTopMargin", "BlockBottomMargin", "BlockLeftMargin", "BlockRightMargin", "TextIndent"}

    def zeichenfarbe(fmt):
        pinsel = fmt.properties.get("ForegroundBrush")
        farbe = fmt.foreground_color
        if isinstance(pinsel, Brush):
            if pinsel.style != 1 or farbe is not None and farbe != pinsel.color:
                return False, None
            farbe = pinsel.color
        elif isinstance(pinsel, Color):
            if farbe is not None and farbe != pinsel:
                return False, None
            farbe = pinsel
        elif pinsel is not None:
            return False, None
        if farbe is not None and (farbe.a != 255 or not all(0 <= v <= 255 for v in (farbe.r, farbe.g, farbe.b))):
            return False, None
        return True, farbe

    font_standard = {"FontCapitalization": 0, "FontLetterSpacing": 0.0, "FontWordSpacing": 0.0, "FontStyleHint": 5,
                     "FontStyleStrategy": 1, "FontKerning": True, "FontHintingPreference": 0, "FontStyleName": "",
                     "FontLetterSpacingType": 0, "FontStretch": 0, "FontOverline": False, "FontStrikeOut": False,
                     "FontFixedPitch": False}

    def zeichen_einfach(fmt, default=False):
        zusatz = {k: v for k, v in fmt.properties.items() if k not in zeichen_schluessel}
        if zusatz and (not default or any(k not in font_standard or font_standard[k] != v for k, v in zusatz.items())):
            return False
        fam = fmt.family
        roh_fam = fmt.properties.get("FontFamilies", fmt.properties.get("FontFamily"))
        if isinstance(roh_fam, (tuple, list)):
            if len(roh_fam) > 1:
                return False
            roh_fam = roh_fam[0] if roh_fam else None
        if fam is not None and roh_fam is not None and fam != roh_fam or roh_fam is not None and not isinstance(roh_fam, str):
            return False
        groesse = fmt.size_pt if fmt.size_pt is not None else fmt.properties.get("FontPointSize")
        gewicht = fmt.weight if fmt.weight is not None else fmt.properties.get("FontWeight")
        kursiv = fmt.italic if fmt.italic is not None else fmt.properties.get("FontItalic")
        unter = fmt.underline if fmt.underline is not None else fmt.properties.get("FontUnderline")
        stil = fmt.properties.get("TextUnderlineStyle", 0)
        if isinstance(stil, bool) or stil not in (0, 1):
            return False
        if gewicht not in (None, 400, 700) or groesse is not None and (not isinstance(groesse, (int, float)) or groesse <= 0):
            return False
        if kursiv is not None and not isinstance(kursiv, bool) or unter is not None and not isinstance(unter, bool):
            return False
        return zeichenfarbe(fmt)[0]

    def absatz_einfach(p):
        f = p.format
        if not set(f.properties) <= absatz_schluessel or not f.visible or f.list_id is not None or f.line_spacing is not None:
            return False
        werte = (f.space_before_px, f.space_after_px, f.left_indent_px, f.right_indent_px, f.first_line_indent_px)
        if any(v is not None and (not isinstance(v, (int, float)) or not isfinite(v)) for v in werte):
            return False
        ausrichtung = f.alignment
        if ausrichtung not in (None, "left", "right", "center", "justify"):
            return False
        if "BlockAlignment" in f.properties:
            try:
                bit = int(f.properties["BlockAlignment"]) & 0xF
            except (ValueError, TypeError):
                return False
            if bit not in (1, 2, 4, 8):
                return False
            ablage = {1: "left", 2: "right", 4: "center", 8: "justify"}[bit]
            if ausrichtung is not None and ausrichtung != ablage:
                return False
        return zeichen_einfach(f.char_format)

    def bild_fuer_export(bild):
        if not isinstance(bild, ModelImage) or not set(bild.format.properties) <= {"ImageName", "ImageWidth", "ImageHeight"}:
            return None
        breite, hoehe = bild.format.properties.get("ImageWidth"), bild.format.properties.get("ImageHeight")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v) or v <= 0 for v in (breite, hoehe)):
            return None
        quelle = (bild.original_format or "").lower()
        if quelle and quelle not in ("png", "jpeg", "jpg"):
            return None
        daten = bild.original if bild.original is not None else bild.raster_png
        if not isinstance(daten, bytes) or not daten:
            return None
        from lunivo_writer.core.document import bildformat
        art = bildformat.format_erkennen(daten)
        if art not in ("png", "jpeg") or quelle and art != ("jpeg" if quelle == "jpg" else quelle):
            return None
        try:
            pruefbild = docx.image.image.Image.from_file(io.BytesIO(daten))
        except Exception:
            return None
        if pruefbild.content_type not in ("image/png", "image/jpeg"):
            return None
        return daten, float(breite), float(hoehe)

    def lauf_einfach(lauf):
        if isinstance(lauf, TextRun):
            return "\x00" not in lauf.text and zeichen_einfach(lauf.format)
        return bild_fuer_export(lauf) is not None

    def tabelle_einfach(tabelle):
        """Nur Tabellen ohne Sonderformate direkt abbilden; komplexe Tabellen gehen an den vollständigen DOCX-Schreiber."""
        if not isinstance(tabelle, Table) or tabelle.rows < 1 or tabelle.columns < 1 \
                or not tabelleigenschaften_einfach(tabelle.properties, tabelle.rows):
            return False
        if tabelle_breiten(tabelle, page) is None:
            return False
        if len(tabelle.table_rows) != tabelle.rows:
            return False
        belegt: set[tuple[int, int]] = set()
        for r, zeile in enumerate(tabelle.table_rows):
            if zeile.minimum_height_px is not None and (isinstance(zeile.minimum_height_px, bool)
                    or not isinstance(zeile.minimum_height_px, (int, float)) or not isfinite(zeile.minimum_height_px)
                    or zeile.minimum_height_px <= 0):
                return False
            if zeile.row_height is not None:
                if zeile.row_height.kind not in ("minimum", "exact") or isinstance(zeile.row_height.value_px, bool) \
                        or not isinstance(zeile.row_height.value_px, (int, float)) or not isfinite(zeile.row_height.value_px) \
                        or zeile.row_height.value_px <= 0:
                    return False
            for zelle in zeile.cells:
                if zelle.row != r or not zellformat_einfach(zelle.properties) or zelle.row_span < 1 or zelle.column_span < 1 \
                        or zelle.column + zelle.column_span > tabelle.columns or zelle.row + zelle.row_span > tabelle.rows:
                    return False
                for rr in range(zelle.row, zelle.row + zelle.row_span):
                    for cc in range(zelle.column, zelle.column + zelle.column_span):
                        if (rr, cc) in belegt:
                            return False
                        belegt.add((rr, cc))
                if any(not isinstance(p, Paragraph) or not absatz_einfach(p) or any(not lauf_einfach(x) for x in p.runs)
                       for p in zelle.content):
                    return False
        return len(belegt) == tabelle.rows * tabelle.columns

    def tabelleigenschaften_einfach(eigenschaften, zeilen):
        erlaubt = {"TableHeaderRowCount", "TableCellPadding", "TableCellSpacing", "FrameBorder", "FrameBorderBrush", "FrameBorderStyle",
                   "FrameWidth", "TableColumnWidthConstraints"}
        if not set(eigenschaften) <= erlaubt:
            return False
        kopfzeilen = eigenschaften.get("TableHeaderRowCount", 0)
        if isinstance(kopfzeilen, bool) or not isinstance(kopfzeilen, int) or not 0 <= kopfzeilen < zeilen:
            return False
        for name in ("TableCellPadding", "TableCellSpacing", "FrameBorder"):
            wert = eigenschaften.get(name, 0.0)
            if isinstance(wert, bool) or not isinstance(wert, (int, float)) or not isfinite(wert) or wert < 0:
                return False
        pinsel = eigenschaften.get("FrameBorderBrush")
        if pinsel is not None and (not isinstance(pinsel, Brush) or pinsel.style != 1 or pinsel.color.a != 255):
            return False
        stil = eigenschaften.get("FrameBorderStyle", 10)
        return not isinstance(stil, bool) and stil in (0, 1, 2, 3, 4, 10)

    def tabelle_breiten(tabelle, seite):
        """Spaltenbreiten in Bildpunkten; feste und prozentuale Vorgaben verteilen den Rest auf variable Spalten."""
        gesamt = float(seite.content_width_px)
        breite = tabelle.properties.get("FrameWidth")
        if breite is not None:
            if not isinstance(breite, Length) or breite.kind not in ("fixed", "percentage", "variable") \
                    or isinstance(breite.value, bool) or not isinstance(breite.value, (int, float)) \
                    or not isfinite(breite.value) or breite.value < 0:
                return None
            if breite.kind == "fixed" and breite.value > 0:
                gesamt = float(breite.value)
            elif breite.kind == "percentage" and breite.value > 0:
                gesamt *= float(breite.value) / 100.0
        vorgaben = tabelle.properties.get("TableColumnWidthConstraints")
        if vorgaben is None:
            return [gesamt / tabelle.columns] * tabelle.columns
        if not isinstance(vorgaben, (tuple, list)) or len(vorgaben) != tabelle.columns:
            return None
        aus = [0.0] * tabelle.columns
        variabel = []
        for i, vorgabe in enumerate(vorgaben):
            if not isinstance(vorgabe, Length) or vorgabe.kind not in ("fixed", "percentage", "variable") \
                    or isinstance(vorgabe.value, bool) or not isinstance(vorgabe.value, (int, float)) \
                    or not isfinite(vorgabe.value) or vorgabe.value < 0:
                return None
            if vorgabe.kind == "fixed":
                aus[i] = float(vorgabe.value)
            elif vorgabe.kind == "percentage":
                aus[i] = gesamt * float(vorgabe.value) / 100.0
            else:
                variabel.append(i)
        fest = sum(aus)
        if variabel:
            rest = max(10.0 * len(variabel), gesamt - fest)
            for i in variabel:
                aus[i] = rest / len(variabel)
        if any(w <= 0 or not isfinite(w) for w in aus):
            return None
        return aus

    def tabelle_breiten_schreiben(ziel, tabelle, breiten):
        twips = [max(1, int(round(w * 15))) for w in breiten]
        tblpr = ziel._tbl.tblPr
        tblw = tblpr.find(qn("w:tblW"))
        if tblw is None:
            tblw = OxmlElement("w:tblW")
            tblpr.insert(0, tblw)
        tblw.set(qn("w:type"), "dxa")
        tblw.set(qn("w:w"), str(sum(twips)))
        for spalte, wert in zip(ziel._tbl.tblGrid.gridCol_lst, twips):
            spalte.set(qn("w:w"), str(wert))
        ziel.autofit = False
        for zeile in tabelle.table_rows:
            for zelle in zeile.cells:
                wert = sum(twips[zelle.column:zelle.column + zelle.column_span])
                tcw = ziel.cell(zelle.row, zelle.column)._tc.get_or_add_tcPr().get_or_add_tcW()
                tcw.set(qn("w:type"), "dxa")
                tcw.set(qn("w:w"), str(wert))

    def tabelleigenschaften_schreiben(ziel, eigenschaften):
        tblpr = ziel._tbl.tblPr
        neu = []
        for name in ("TableCellSpacing", "TableCellPadding"):
            wert = float(eigenschaften.get(name, 0.0))
            if wert <= 0:
                continue
            if name == "TableCellSpacing":
                abstand = OxmlElement("w:tblCellSpacing")
                abstand.set(qn("w:w"), str(int(round(wert * 15))))
                abstand.set(qn("w:type"), "dxa")
                neu.append(abstand)
            else:
                raender = OxmlElement("w:tblCellMar")
                for kante in ("top", "left", "bottom", "right"):
                    rand = OxmlElement(f"w:{kante}")
                    rand.set(qn("w:w"), str(int(round(wert * 15))))
                    rand.set(qn("w:type"), "dxa")
                    raender.append(rand)
                neu.append(raender)
        breite = float(eigenschaften.get("FrameBorder", 0.0))
        stil = eigenschaften.get("FrameBorderStyle", 10)
        if breite > 0 and stil != 0:
            pinsel = eigenschaften.get("FrameBorderBrush")
            farbe = pinsel.color if isinstance(pinsel, Brush) else Color(0, 0, 0)
            wert = {1: "dotted", 2: "dashed", 3: "single", 4: "double", 10: "single"}[stil]
            raender = OxmlElement("w:tblBorders")
            for kante in ("top", "left", "bottom", "right", "insideH", "insideV"):
                rand = OxmlElement(f"w:{kante}")
                rand.set(qn("w:val"), wert)
                rand.set(qn("w:sz"), str(max(2, int(round(breite * 6)))))
                rand.set(qn("w:space"), "0")
                rand.set(qn("w:color"), f"{farbe.r:02X}{farbe.g:02X}{farbe.b:02X}")
                raender.append(rand)
            neu.insert(1 if neu and neu[0].tag == qn("w:tblCellSpacing") else 0, raender)
        look = tblpr.find(qn("w:tblLook"))
        for element in neu:
            look.addprevious(element) if look is not None else tblpr.append(element)

    def zellformat_einfach(eigenschaften):
        if not set(eigenschaften) <= {"BackgroundBrush", "TableCellVerticalAlignment"}:
            return False
        pinsel = eigenschaften.get("BackgroundBrush")
        if pinsel is not None and (not isinstance(pinsel, Brush) or pinsel.style != 1 or pinsel.color.a != 255):
            return False
        ausrichtung = eigenschaften.get("TableCellVerticalAlignment", 0)
        return not isinstance(ausrichtung, bool) and ausrichtung in (0, 3, 4, 5, 6)

    def zellformat_schreiben(ziel, eigenschaften):
        pinsel = eigenschaften.get("BackgroundBrush")
        tcpr = ziel._tc.get_or_add_tcPr()
        if isinstance(pinsel, Brush):
            schattierung = OxmlElement("w:shd")
            schattierung.set(qn("w:val"), "clear")
            schattierung.set(qn("w:color"), "auto")
            schattierung.set(qn("w:fill"), f"{pinsel.color.r:02X}{pinsel.color.g:02X}{pinsel.color.b:02X}")
            tcpr.append(schattierung)
        ausrichtung = eigenschaften.get("TableCellVerticalAlignment", 0)
        wert = {0: "top", 3: "center", 4: "top", 5: "bottom", 6: "top"}.get(ausrichtung)
        if wert is not None and ausrichtung != 0:
            vertikal = OxmlElement("w:vAlign")
            vertikal.set(qn("w:val"), wert)
            tcpr.append(vertikal)

    def block_einfach(block):
        if isinstance(block, Paragraph):
            return absatz_einfach(block) and all(lauf_einfach(r) for r in block.runs)
        return tabelle_einfach(block)

    if not zeichen_einfach(modell.default_format, default=True):
        return None
    if any(not block_einfach(block) for block in section.content):
        return None

    try:
        d = docx.Document()
        s = d.sections[0]
        s.page_width, s.page_height = Mm(page.width_mm), Mm(page.height_mm)
        s.top_margin, s.bottom_margin = Mm(page.margin_top_mm), Mm(page.margin_bottom_mm)
        s.left_margin, s.right_margin = Mm(page.margin_left_mm), Mm(page.margin_right_mm)
        normal = d.styles["Normal"].font
        d.styles["Normal"].paragraph_format.space_before = Pt(0)
        d.styles["Normal"].paragraph_format.space_after = Pt(0)

        def format_schreiben(font, fmt):
            fam = fmt.family or fmt.properties.get("FontFamilies", fmt.properties.get("FontFamily"))
            if isinstance(fam, (tuple, list)):
                fam = fam[0] if fam else None
            groesse = fmt.size_pt if fmt.size_pt is not None else fmt.properties.get("FontPointSize")
            gewicht = fmt.weight if fmt.weight is not None else fmt.properties.get("FontWeight")
            kursiv = fmt.italic if fmt.italic is not None else fmt.properties.get("FontItalic")
            unter = fmt.underline if fmt.underline is not None else fmt.properties.get("FontUnderline")
            if fam:
                font.name = fam
            if groesse is not None:
                font.size = Pt(float(groesse))
            if gewicht is not None:
                font.bold = int(gewicht) >= 700
            if kursiv is not None:
                font.italic = kursiv
            if unter is not None or "TextUnderlineStyle" in fmt.properties:
                font.underline = bool(unter) or fmt.properties.get("TextUnderlineStyle", 0) == 1
            _ok, farbe = zeichenfarbe(fmt)
            if farbe is not None:
                font.color.rgb = RGBColor(farbe.r, farbe.g, farbe.b)

        format_schreiben(normal, modell.default_format)
        def absatz_schreiben(p, ziel):
            ausrichtung = p.format.alignment
            if ausrichtung is None and "BlockAlignment" in p.format.properties:
                ausrichtung = {1: "left", 2: "right", 4: "center", 8: "justify"}[int(p.format.properties["BlockAlignment"]) & 0xF]
            ziel.alignment = {"left": WD_ALIGN_PARAGRAPH.LEFT, "right": WD_ALIGN_PARAGRAPH.RIGHT,
                              "center": WD_ALIGN_PARAGRAPH.CENTER, "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}.get(ausrichtung)
            pf = ziel.paragraph_format
            for name, attr in (("left_indent_px", "left_indent"), ("right_indent_px", "right_indent"),
                               ("first_line_indent_px", "first_line_indent"), ("space_before_px", "space_before"), ("space_after_px", "space_after")):
                value = getattr(p.format, name)
                if value is None:
                    eigenschaft = {"left_indent_px": "BlockLeftMargin", "right_indent_px": "BlockRightMargin", "first_line_indent_px": "TextIndent",
                                   "space_before_px": "BlockTopMargin", "space_after_px": "BlockBottomMargin"}[name]
                    value = p.format.properties.get(eigenschaft)
                if value is not None:
                    setattr(pf, attr, Pt(float(value) * 0.75))
            laeufe = p.runs or ([TextRun("", p.format.char_format)] if p.format.char_format != type(p.format.char_format)() else [])
            for t in laeufe:
                run = ziel.add_run()
                if isinstance(t, ModelImage):
                    daten, breite, hoehe = bild_fuer_export(t)
                    run.add_picture(io.BytesIO(daten), width=Emu(round(breite * EMU_PER_PX)), height=Emu(round(hoehe * EMU_PER_PX)))
                else:
                    run.text = t.text
                    format_schreiben(run.font, t.format)

        if not section.content:
            d.add_paragraph()
        for block in section.content:
            if isinstance(block, Paragraph):
                absatz_schreiben(block, d.add_paragraph())
                continue
            ziel = d.add_table(rows=block.rows, cols=block.columns)
            tabelleigenschaften_schreiben(ziel, block.properties)
            kopfzeilen = int(block.properties.get("TableHeaderRowCount", 0))
            for index, zeile in enumerate(block.table_rows):
                hoehe = zeile.row_height.value_px if zeile.row_height is not None else zeile.minimum_height_px
                if hoehe is not None:
                    ziel.rows[index].height = Pt(float(hoehe) * 0.75)
                    art = zeile.row_height.kind if zeile.row_height is not None else "minimum"
                    ziel.rows[index].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY if art == "exact" else WD_ROW_HEIGHT_RULE.AT_LEAST
                if index < kopfzeilen:
                    ziel.rows[index]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
            for zeile in block.table_rows:
                for zelle in zeile.cells:
                    z = ziel.cell(zelle.row, zelle.column)
                    zellformat_schreiben(z, zelle.properties)
                    if zelle.content:
                        absatz_schreiben(zelle.content[0], z.paragraphs[0])
                        for p in zelle.content[1:]:
                            absatz_schreiben(p, z.add_paragraph())
            for zeile in block.table_rows:
                for zelle in zeile.cells:
                    if zelle.row_span > 1 or zelle.column_span > 1:
                        ziel.cell(zelle.row, zelle.column).merge(
                            ziel.cell(zelle.row + zelle.row_span - 1, zelle.column + zelle.column_span - 1))
            tabelle_breiten_schreiben(ziel, block, tabelle_breiten(block, page))
        d.core_properties.title = m.get("title", "") or ""
        d.core_properties.author = m.get("author", "") or "Lunivo Writer"
        kennung = m.get("sprache") or str(getattr(page, "silben_sprache", "") or "").replace("_", "-")
        if kennung:
            rpr = d.styles.element.find(qn("w:docDefaults") + "/" + qn("w:rPrDefault") + "/" + qn("w:rPr"))
            if rpr is not None:
                lang = rpr.find(qn("w:lang"))
                if lang is None:
                    lang = OxmlElement("w:lang")
                    rpr.append(lang)
                lang.set(qn("w:val"), kennung)
        out = io.BytesIO()
        d.save(out)
        return out.getvalue(), IOReport()
    except Exception as e:
        logging.getLogger("lunivo.dateien").exception("DOCX-Modell konnte nicht aufgebaut werden")
        raise DocumentIOError(f"Das Dokument konnte nicht als DOCX aufgebaut werden: {e}") from e


def write_docx(path: str, qdoc: QTextDocument, page: PageSettings, meta: Optional[dict] = None, sicherung: bool = True) -> IOReport:
    """Schreibt über den sicheren Schreibweg (Temp-Datei, Prüfung, Umbenennen). Wirft DocumentIOError."""
    from lunivo_writer.dienste import sicher_schreiben
    data, report = docx_daten(qdoc, page, meta)
    sicher_schreiben.bytes_schreiben(path, data, endung=".docx", sicherung=sicherung)
    return report
