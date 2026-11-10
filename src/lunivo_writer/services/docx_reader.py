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
from lunivo_writer.services.docx_teile.lesen_textfelder import TextfeldMixin
from lunivo_writer.services.docx_teile.lesen_metadaten import LesenMetadatenMixin
from lunivo_writer.services.docx_teile.lesen_absatz import LesenAbsatzMixin
from lunivo_writer.services.docx_teile.lesen_runs import LesenRunsMixin



class _Reader(LesenMetadatenMixin, LesenAbsatzMixin, LesenRunsMixin, StilMixin, TabellenMixin, SeiteMixin, ObjekteMixin, TextfeldMixin):
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



    def run(self):
        self._nicht_unterstuetztes_melden(self.d.element.body)
        self._erste_seite = self.read_page()
        self._koerper_lesen(self.d.element.body)
        self._ketten_bereinigen()
        # leeren Schlussblock nach Tabelle behalten (Qt braucht ihn)
        df = QFont(self.def_font or "Calibri")
        df.setPointSizeF(self.def_size or 11.0)
        self.doc.setDefaultFont(df)
        meta = self._meta_lesen()
        self.doc.setModified(False)
        return self.doc, self._erste_seite, meta, self.report

    def _nicht_unterstuetztes_melden(self, body) -> None:
        for pat, msg in _UNSUPPORTED:
            try:
                if _xp(body, pat):
                    self.report.warn(msg)
            except Exception:
                pass

    def _koerper_lesen(self, body) -> None:
        for child in _kinder(body):
            if child.tag == qn("w:p"):
                self.fresh = self.add_paragraph(Paragraph(child, self.d._body), self.cur, reuse=self.fresh)
            elif child.tag == qn("w:tbl"):
                self.add_table(Table(child, self.d._body))

    def _meta_lesen(self) -> dict:
        props = self.d.core_properties
        meta = {"title": props.title or "", "author": props.author or ""}
        meta.update(self.zus)
        lang = self.d.styles.element.find(qn("w:docDefaults") + "/" + qn("w:rPrDefault") + "/" + qn("w:rPr") + "/" + qn("w:lang"))
        if lang is not None and lang.get(qn("w:val")):
            meta["sprache"] = lang.get(qn("w:val"))
        return meta


def _kinder(eltern):
    """Die Blockelemente eines Körpers; Inhaltssteuerelemente (``w:sdt``) werden aufgelöst."""
    for c in eltern.iterchildren():
        if c.tag == qn("w:sdt"):
            inhalt = c.find(qn("w:sdtContent"))
            if inhalt is not None:
                yield from _kinder(inhalt)
        else:
            yield c


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
