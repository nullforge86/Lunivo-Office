"""QTextDocument → DOCX (python-docx).

Schreibt Absätze, Überschriften (Formatvorlagen „Heading n“), Titel/Untertitel/
Zitat, Zeichenformat, Ausrichtung, Einzüge, Abstände, Zeilenabstand, Listen,
Seitenumbrüche, Tabellen (mit verbundenen Zellen), Bilder, Hyperlinks,
Seitengröße, Ränder, Kopf- und Fußzeile (mit Seitenzahlfeld).
"""
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
from lunivo_writer.services.docx_teile.schreiben_seite import SeiteSchreiber
from lunivo_writer.services.docx_teile.schreiben_tabellen import TabellenSchreiber
from lunivo_writer.services.docx_teile.schreiben_objekte import ObjekteSchreiber
from lunivo_writer.services.docx_teile.schreiben_zusatz import ZusatzSchreiber
from lunivo_writer.services.docx_teile.schreiben_dokument import SchreibenDokumentMixin
from lunivo_writer.services.docx_teile.schreiben_absatz import SchreibenAbsatzMixin
from lunivo_writer.services.docx_teile.schreiben_runs import SchreibenRunsMixin



class _Writer(SchreibenDokumentMixin, SchreibenAbsatzMixin, SchreibenRunsMixin, SeiteSchreiber, TabellenSchreiber, ObjekteSchreiber, ZusatzSchreiber):
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





    def _fldchar(para, typ: str):
        r = OxmlElement("w:r")
        fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), typ)
        r.append(fc)
        para._p.append(r)

    def _instr(para, text: str):
        r = OxmlElement("w:r")
        it = OxmlElement("w:instrText"); it.set("{http://www.w3.org/XML/1998/namespace}space", "preserve"); it.text = f" {text} "
        r.append(it)
        para._p.append(r)










    def _kompatibilitaet(self) -> None:
        gewaehlt = set(self.meta.get("kompat") or [])
        einst = self.d.settings.element
        if "bilder_komprimieren" in self.meta:
            wort = einst.find(qn("w:doNotAutoCompressPictures"))
            if self.meta["bilder_komprimieren"] and wort is not None:
                einst.remove(wort)                                    # Word darf Bilder beim Speichern selbst komprimieren
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
        # Word verlangt nach einer Tabelle einen Absatz; leere Endabsätze sonst entfernen
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


def write_docx(path: str, qdoc: QTextDocument, page: PageSettings, meta: Optional[dict] = None, sicherung: bool = True) -> IOReport:
    """Schreibt über den sicheren Schreibweg (Temp-Datei, Prüfung, Umbenennen). Wirft DocumentIOError."""
    from lunivo_writer.services import sicher_schreiben
    data, report = docx_daten(qdoc, page, meta)
    sicher_schreiben.bytes_schreiben(path, data, endung=".docx", sicherung=sicherung)
    return report
