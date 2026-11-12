"""DOCX → ``core.document.Document`` direkt, ohne ``QTextDocument`` als Zwischenschritt (Phase 5b der Qt-Entkopplung).

Der Leser nutzt die bestehende Auswertung (Formatvorlagen, Einzüge, Abstände, Schrift …) des ``docx_leser._Reader`` und lässt ihn in einen ``ModellCursor`` schreiben statt in einen
``QTextCursor``. Der ``ModellCursor`` kennt nur, was in das Modell überführt ist; jeder andere Aufruf (Tabelle, Bild, Rahmen, Auswahl …) löst ``NichtImModell`` aus, und ``lese_docx_modell``
liefert dann ``None`` — der Aufrufer nimmt den alten Weg. So wächst der Umfang Stück für Stück, ohne dass ein Dokument unvollständig gelesen wird.

Stand: Absätze (Formate, Listen, Abschnittsmarken, Seitenumbrüche) und Textstücke (Text, Tabulator, Zeilenumbruch, Notenmarken, Verweise, Textmarken, Änderungsverfolgung).
Dazu: Tabellen (Zellinhalt, Verbinden, Formate über eine Hilfstabelle), Bilder in der Zeile, XE-Stichworte (außerhalb von Zellen).
Noch nicht: Zeilenhöhen nach Textmaß (Phase 6), Formen, Rahmen, Textfelder, Verweise mit Nachbearbeitung, Positionen für schwebende Bilder."""
from __future__ import annotations

from PySide6.QtGui import QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextImageFormat, QTextLength, QTextTableCellFormat

from lunivo_writer.adapter.qt.dokument import (absatzformat_aus_qt, bild_aus_format, document_from_qt, eigenschaften,
                                               schnitte_bilden, zeichenformat_aus_qt)
from lunivo_writer.core.document import CharacterFormat, ListFormat, Paragraph, ParagraphFormat, RowHeight, Table, TableCell, TableRow, TextRun
from lunivo_writer.core.textlayout import FontSpec
from lunivo_writer.dienste import docx_leser
from lunivo_writer.editor.seite import abschnitte as AB


class NichtImModell(Exception):
    """Der Leser braucht etwas, das das Modell an dieser Stelle noch nicht aufnimmt."""


class _Absatz:
    def __init__(self, bf: QTextBlockFormat, cf: QTextCharFormat):
        self.bf, self.cf = bf, cf
        self.runs: list[tuple[str, QTextCharFormat, int]] = []       # (Text, Format, Stelle im Dokument); ein Bild steht als ("\ufffc", Bildformat)
        self.list_id: int | None = None


class _Fertig:
    """Ein schon fertiger Block des Modells (zum Beispiel ein schwebendes Bild mit seinem Anker), der vor dem aktuellen Absatz steht."""

    def __init__(self, block):
        self.block = block


class _BlockRef:
    def __init__(self, a: _Absatz):
        self.a = a

    def isValid(self) -> bool:
        return True

    def blockFormat(self) -> QTextBlockFormat:
        return QTextBlockFormat(self.a.bf)

    def __getattr__(self, name: str):
        raise NichtImModell(f"block.{name}")


class _ListRef:
    def __init__(self, nummer: int):
        self.nummer = nummer

    def add(self, block: _BlockRef) -> None:
        block.a.list_id = self.nummer


class _ZelleRef:
    """Eine Zelle der Tabelle: Format und Verbundenes rechnet die Zelle der Hilfstabelle (``_TabelleRef``), der Inhalt geht in eine eigene Schreibmarke."""

    def __init__(self, tabelle: "_TabelleRef", zelle):
        self._t, self._z = tabelle, zelle

    def firstCursorPosition(self) -> "ModellCursor":
        return self._t.inhalt(self._z.row(), self._z.column())

    def lastCursorPosition(self):
        raise NichtImModell("cell.lastCursorPosition")

    def begin(self):
        raise NichtImModell("cell.begin")                  # nur für Zeilenhöhen nach Textmaß: braucht den Textsatz (Phase 6)

    def __getattr__(self, name: str):
        return getattr(self._z, name)


class _TabelleRef:
    """Eine Tabelle im Modell. Formate, Verbinden und Zellformate rechnet eine kleine Hilfstabelle von Qt (wie bisher, nur ohne Inhalt); der Inhalt jeder Zelle steht in einer eigenen Schreibmarke."""

    def __init__(self, rows: int, cols: int, tf, bilder: QTextDocument):
        self._bilder = bilder
        self._doc = QTextDocument()
        self._qt = QTextCursor(self._doc).insertTable(rows, cols, tf)
        self._inhalte: dict[tuple[int, int], ModellCursor] = {}

    def inhalt(self, r: int, c: int) -> "ModellCursor":
        if (r, c) not in self._inhalte:
            self._inhalte[(r, c)] = ModellCursor(self._bilder, verschachtelt=True, erstes_zeichenformat=lambda cf: self._zellformat_ersetzen(r, c, cf))
        return self._inhalte[(r, c)]

    def _zellformat_ersetzen(self, r: int, c: int, cf: QTextCharFormat) -> None:
        """Wie in Qt: Das Zeichenformat des ersten Absatzes einer Zelle ist das Format der Zelle selbst; es setzt ein früheres Zellformat zurück."""
        neu = QTextTableCellFormat()
        neu.merge(cf)
        self._qt.cellAt(r, c).setFormat(neu)

    def cellAt(self, r: int, c: int) -> _ZelleRef:
        return _ZelleRef(self, self._qt.cellAt(r, c))

    def __getattr__(self, name: str):
        return getattr(self._qt, name)

    def als_modell(self) -> Table:
        from lunivo_writer.core.layout.seitenumbruch import P_ZEILE_HOEHE_ART, P_ZEILE_MINHOEHE
        qt = self._qt
        tab = Table(qt.rows(), qt.columns(), eigenschaften(qt.format()))
        for r in range(qt.rows()):
            zeile = TableRow()
            for c in range(qt.columns()):
                z = qt.cellAt(r, c)
                if z.isValid() and z.row() == r and z.column() == c:
                    inhalt = self._inhalte.get((r, c))
                    props = eigenschaften(z.format())
                    bloecke = inhalt.als_modell() if inhalt is not None else [Paragraph()]
                    if bloecke and isinstance(bloecke[0], Paragraph):
                        bloecke[0].format.char_format = CharacterFormat(dict(props))           # in Qt ist es dasselbe Format wie das der Zelle
                    zeile.cells.append(TableCell(r, c, z.rowSpan(), z.columnSpan(), props, bloecke))
            werte = [z.properties.get(P_ZEILE_MINHOEHE) for z in zeile.cells]
            werte = [v for v in werte if isinstance(v, (int, float)) and v > 0]
            zeile.minimum_height_px = max(werte) if werte else None
            art = next((z.properties.get(P_ZEILE_HOEHE_ART) for z in zeile.cells if z.properties.get(P_ZEILE_HOEHE_ART) in ("minimum", "exact")), None)
            if zeile.minimum_height_px is not None:
                zeile.row_height = RowHeight(art or "minimum", zeile.minimum_height_px)
            tab.table_rows.append(zeile)
        return tab


class ModellCursor:
    """Die Schreibmarke des Lesers, aber in das Modell: Absätze mit Textstücken, Listen, Tabellen und Zählung der Position wie bei Qt."""

    def __init__(self, doc: QTextDocument, verschachtelt: bool = False, erstes_zeichenformat=None):
        self._doc = doc                                                       # hält die Bilder (Ressourcen) des Lesers
        self._erstes = erstes_zeichenformat
        self.elemente: list = [_Absatz(QTextBlockFormat(), QTextCharFormat())]       # _Absatz oder _TabelleRef in Dokumentreihenfolge
        self.listen: dict[int, object] = {}
        self._pos = 0
        self._verschachtelt = verschachtelt

    def _aktuell(self) -> _Absatz:
        return self.elemente[-1]

    def insertTable(self, rows: int, cols: int, tf) -> _TabelleRef:
        """Wie Qt: die Tabelle steht nach dem aktuellen Absatz, danach folgt ein leerer Absatz."""
        t = _TabelleRef(rows, cols, tf, self._doc)
        self.elemente.append(t)
        self.elemente.append(_Absatz(QTextBlockFormat(), QTextTableCellFormat()))           # in Qt trägt der Absatz nach einer Tabelle ein Zellformat als Zeichenformat
        return t

    def als_modell(self) -> list:
        """Die Blöcke als Modell (Absätze und Tabellen)."""
        aus = []
        for e in self.elemente:
            if isinstance(e, _Fertig):
                aus.append(e.block)
            elif isinstance(e, _TabelleRef):
                aus.append(e.als_modell())
            else:
                runs = [bild_aus_format(cf, self._doc) if cf.isImageFormat() else TextRun(t, zeichenformat_aus_qt(cf)) for t, cf, _st in e.runs if t]
                aus.append(Paragraph(absatzformat_aus_qt(e.bf, zeichenformat_aus_qt(e.cf), e.list_id, True), runs))
        return aus

    def vorab_einfuegen(self, bloecke: list, zeichen: int) -> None:
        """Fertige Blöcke vor den aktuellen Absatz setzen; ``zeichen`` = so viele Stellen belegen sie im Qt-Dokument (die Zählung der Position bleibt wie bei Qt)."""
        self.elemente[-1:-1] = [_Fertig(b) for b in bloecke]
        self._pos += zeichen

    def insertImage(self, fmt) -> None:
        a = self._aktuell()
        a.runs.append(("\ufffc", QTextImageFormat(fmt), self._pos))
        self._pos += 1

    def insertBlock(self, bf: QTextBlockFormat | None = None, cf: QTextCharFormat | None = None) -> None:
        a = self._aktuell()
        letzter = a.runs[-1][1] if a.runs else a.cf
        self.elemente.append(_Absatz(QTextBlockFormat(bf) if bf is not None else QTextBlockFormat(a.bf),
                                     QTextCharFormat(cf) if cf is not None else QTextCharFormat(letzter)))
        self._pos += 1

    def insertText(self, text: str, cf: QTextCharFormat | None = None) -> None:
        a = self._aktuell()
        a.runs.append((text, QTextCharFormat(cf) if cf is not None else QTextCharFormat(a.runs[-1][1] if a.runs else a.cf), self._pos))
        self._pos += len(text)

    def format_bereich(self, von: int, bis: int, nf: QTextCharFormat) -> None:
        """Wie ``QTextCursor.mergeCharFormat`` über [von, bis): die Textstücke werden an den Grenzen geteilt, nur der markierte Teil bekommt ``nf``."""
        for a in self.elemente:
            if not isinstance(a, _Absatz):
                continue
            neu = []
            for text, cf, st in a.runs:
                ende = st + len(text)
                if ende <= von or st >= bis or cf.isImageFormat() or not text:
                    neu.append((text, cf, st))
                    continue
                a0, a1 = max(von, st) - st, min(bis, ende) - st
                if a0 > 0:
                    neu.append((text[:a0], cf, st))
                mitte = QTextCharFormat(cf)
                mitte.merge(nf)
                neu.append((text[a0:a1], mitte, st + a0))
                if a1 < len(text):
                    neu.append((text[a1:], cf, st + a1))
            a.runs = neu

    def setBlockFormat(self, bf: QTextBlockFormat) -> None:
        self._aktuell().bf = QTextBlockFormat(bf)

    def setBlockCharFormat(self, cf: QTextCharFormat) -> None:
        if self._erstes is not None and len(self.elemente) == 1:
            self._erstes(cf)
        self._aktuell().cf = QTextCharFormat(cf)

    def mergeBlockFormat(self, bf: QTextBlockFormat) -> None:
        self._aktuell().bf.merge(bf)

    def blockFormat(self) -> QTextBlockFormat:
        return QTextBlockFormat(self._aktuell().bf)

    def block(self) -> _BlockRef:
        return _BlockRef(self._aktuell())

    def createList(self, lf) -> _ListRef:
        nummer = len(self.listen) + 1
        self.listen[nummer] = lf
        self._aktuell().list_id = nummer
        return _ListRef(nummer)

    def position(self) -> int:
        return self._pos

    def __getattr__(self, name: str):
        raise NichtImModell(name)


class _ModellReader(docx_leser._Reader):
    """Der alte Leser mit einer Modell-Schreibmarke."""

    def __init__(self, path: str):
        super().__init__(path)
        self.cur = ModellCursor(self.doc)
        self._zellen_tiefe = 0                             # Verschachtelung der Tabellenzellen, in denen gerade gelesen wird

    @staticmethod
    def _zelle_ende(qt, r0: int, c0: int):
        return qt.inhalt(r0, c0)                                   # die Schreibmarke der Zelle steht schon hinter der verschachtelten Tabelle

    def _schwebend_setzen(self, cursor, imf, seite: str, versatz: float) -> None:
        """Das umflossene Bild als Schwebeobjekt (Anker-Absatz und Rahmen mit dem Bild) vor den aktuellen Absatz des Modells setzen. Die Form von Anker und Rahmen baut dieselbe
        Funktion wie im Qt-Dokument (``umbruch.schwebend_einfuegen``), auf einem leeren Hilfsdokument; das Ergebnis geht über die Brücke ins Modell."""
        from PySide6.QtCore import QUrl
        from lunivo_writer.adapter.qt.dokument import document_from_qt
        from lunivo_writer.editor.seite.umbruch import schwebend_einfuegen
        hilfe = QTextDocument()
        bild = self.doc.resource(QTextDocument.ImageResource, QUrl(imf.name()))
        if bild is not None:
            hilfe.addResource(QTextDocument.ImageResource, QUrl(imf.name()), bild)
        c = QTextCursor(hilfe)                                      # der Anker-Absatz erbt Absatz- und Zeichenformat des Absatzes, vor dem das Bild eingefügt wird
        c.setBlockFormat(cursor.blockFormat())
        c.setBlockCharFormat(cursor._aktuell().cf)
        schwebend_einfuegen(hilfe, 0, imf, seite, versatz)
        bloecke = document_from_qt(hilfe).sections[0].content
        cursor.vorab_einfuegen(bloecke[:2], hilfe.characterCount() - 1)
        cursor._aktuell().bf = QTextBlockFormat()                   # wie in Qt: der Absatz nach dem Rahmen ist ein neuer Block ohne Absatz- und Zeichenformat
        cursor._aktuell().cf = QTextCharFormat()

    def _zeilenhoehen(self, qt, table) -> None:
        """w:trHeight je Zeile als Mindesthöhe übernehmen (wie der alte Leser); die Höhe des Zellinhalts kommt hier aus dem Qt-freien Textsatz (``core.layout``) statt aus dem Qt-Layout."""
        if not hasattr(qt, "_inhalte"):                              # verschachtelte Tabelle auf dem Hilfsdokument: eine echte Qt-Tabelle, wie im alten Leser
            super()._zeilenhoehen(qt, table)
            return
        from PySide6.QtGui import QTextFrameFormat
        from lunivo_writer.core.document import Document
        from lunivo_writer.core.layout import hoehe_von_bloecken
        from lunivo_writer.dienste.textsatz import standard_engine
        from lunivo_writer.editor.tabelle.tabelleneigenschaften import zeilenhoehe_setzen
        from lunivo_writer.core.layout.seitenumbruch import P_ZEILE_HOEHE_ART
        from lunivo_writer.modelle.seite import mm_to_px
        if qt.frameFormat().position() != QTextFrameFormat.InFlow:
            return
        grund = self.doc.defaultFont()
        dok = Document(default_format=CharacterFormat({"FontFamilies": (grund.family(),), "FontPointSize": grund.pointSizeF() if grund.pointSizeF() > 0 else 11.0}))
        engine = standard_engine()
        tf = qt.format()
        gesamt = getattr(self._erste_seite, "content_width_px", 600.0)
        spalten = max(1, qt.columns())
        constraints = tf.columnWidthConstraints()
        pad = max(0.0, tf.cellPadding())
        for r, row in enumerate(table.rows):
            h = row._tr.xpath("w:trPr/w:trHeight/@w:val")
            rules = row._tr.xpath("w:trPr/w:trHeight/@w:hRule")
            try:
                tw = float(h[0]) if h else 0.0
            except ValueError:
                continue
            if tw <= 0:
                continue
            c = constraints[0] if constraints else None
            breite = c.rawValue() if c is not None and c.type() == QTextLength.FixedLength else gesamt * c.rawValue() / 100 if c is not None and c.type() == QTextLength.PercentageLength else gesamt / spalten
            inhalt_ref = qt._inhalte.get((r, 0))
            inhalt = 0.0
            if inhalt_ref is not None:
                bloecke = inhalt_ref.als_modell()
                if any(getattr(b, "text", "").strip() for b in bloecke):                    # nur Zellen mit Text: leere Zellen messen wie im alten Leser mit der Standardschrift
                    inhalt = hoehe_von_bloecken(dok, engine, bloecke, max(10.0, breite - 2 * pad))
            px = mm_to_px(tw / 1440 * 25.4)
            zeilenhoehe_setzen(qt, r, px, inhalt or engine.font_metrics(FontSpec(grund.family(), max(1.0, grund.pointSizeF()))).line_spacing)
            art = "exact" if rules and rules[0] == "exact" else "minimum"
            for c in range(qt.columns()):
                cell = qt._qt.cellAt(r, c)
                if cell.isValid() and cell.row() == r:
                    f = cell.format().toTableCellFormat()
                    f.setProperty(int(P_ZEILE_HOEHE_ART.split(":")[1]), art)
                    cell.setFormat(f)

    @staticmethod
    def _block_format_setzen(block, vf) -> None:
        block.a.bf = QTextBlockFormat(vf)

    def _feld_ende(self) -> None:
        """XE-Stichworte: die Markierung des zuletzt eingefügten Textes im Modell setzen (wie ``_feld_ende`` des alten Lesers). Liegt die Stelle in
        einer Tabellenzelle, bleibt es beim alten Leser (die Stellen der Zellen sind dort anders gezählt)."""
        f, self._feld = self._feld, None
        if not f:
            return
        teile = f["instr"].split()
        if not (teile and teile[0].upper() == "XE" and self._letzter):
            return
        if self._zellen_tiefe:
            raise NichtImModell("feld in Zelle")
        from lunivo_writer.editor.dokument.indexeintrag import aus_feld
        from lunivo_writer.editor.dokument.zusatz import P_INDEX, P_INDEX_OPT
        e = aus_feld(f["instr"])
        if e is None:
            return
        nf = QTextCharFormat(); nf.setProperty(P_INDEX, e.text())
        if e.schalter():
            nf.setProperty(P_INDEX_OPT, e.schalter())
        self.cur.format_bereich(self._letzter[0], self._letzter[1], nf)

    def _zelle_fuellen(self, qt, r0: int, c0: int, cell) -> None:
        self._zellen_tiefe += 1
        try:
            if any(isinstance(item, docx_leser.Table) for item in cell.iter_inner_content()):
                self._zelle_mit_tabelle(qt, r0, c0, cell)
            else:
                super()._zelle_fuellen(qt, r0, c0, cell)
        finally:
            self._zellen_tiefe -= 1

    def _zelle_mit_tabelle(self, qt, r0: int, c0: int, cell) -> None:
        """Zelle mit verschachtelter Tabelle: der Inhalt wird mit dem Leser auf einem Hilfsdokument gebaut (Qt legt Absatz, Tabelle und den Absatz dahinter so an, wie der alte Leser es
        immer getan hat) und geht über die Brücke als fertige Blöcke ins Modell. Die Bilder des Hilfsdokuments liegen im Ressourcenspeicher des Lesers."""
        from PySide6.QtCore import QUrl
        from lunivo_writer.adapter.qt.dokument import document_from_qt
        hilfe = QTextDocument()
        ccur = QTextCursor(hilfe)
        first = True
        for item in cell.iter_inner_content():
            if isinstance(item, docx_leser.Paragraph):
                self.add_paragraph(item, ccur, reuse=first, in_table=True)
                first = False
            elif isinstance(item, docx_leser.Table):
                self.add_table(item, cursor=ccur)
                ccur = QTextCursor(hilfe)
                ccur.movePosition(QTextCursor.End)
                ccur.insertBlock()
                first = False
        b = hilfe.begin()
        namen = set()
        while b.isValid():
            it = b.begin()
            while not it.atEnd():
                cf = it.fragment().charFormat()
                if cf.isImageFormat():
                    namen.add(cf.toImageFormat().name())
                it += 1
            b = b.next()
        for n in namen:
            bild = self.doc.resource(QTextDocument.ImageResource, QUrl(n))
            if bild is not None:
                hilfe.addResource(QTextDocument.ImageResource, QUrl(n), bild)
        qt._zellformat_ersetzen(r0, c0, QTextCursor(hilfe.firstBlock()).blockCharFormat())
        inhalt = qt.inhalt(r0, c0)
        inhalt.elemente = [_Fertig(blk) for blk in document_from_qt(hilfe).sections[0].content]

    def _cursor_ans_ende(self) -> None:
        pass                                              # die Schreibmarke steht nach einer Tabelle schon im leeren Absatz dahinter

    def _ketten_bereinigen(self) -> None:
        pass                                              # betrifft nur Textfelder, die dieser Leser noch nicht liest

    def run_modell(self):
        self._nicht_unterstuetztes_melden(self.d.element.body)
        self._erste_seite = self.read_page()
        self._koerper_lesen(self.d.element.body)
        self._ketten_bereinigen()
        df = docx_leser.QFont(self._standard_schrift() or "Calibri")
        df.setPointSizeF(self.def_size or 11.0)
        self.doc.setDefaultFont(df)
        meta = self._meta_lesen()
        modell = document_from_qt(self.doc, self._erste_seite)           # Grundeinstellungen des Dokuments (Grundschrift, Rand, Textsatz); self.doc hat sonst keinen Inhalt
        from lunivo_writer.core.document import Footnote
        modell.notes = [Footnote(int(nid), art, str(text))
                        for art, eintraege in meta.get("noten", {}).items() if art in ("f", "e")
                        for nid, text in eintraege.items()]
        oben, marken, listen = [], [], {}
        for e, p in zip(self.cur.elemente, self.cur.als_modell()):
            if isinstance(e, _Absatz) and e.bf.hasProperty(AB.B_ABSCHNITT):
                marken_wert = AB.lesen(e.bf)
                p.format.properties.pop(f"user:{int(AB.B_ABSCHNITT)}", None)
                oben.append(p)
                marken.append((len(oben), marken_wert))
            else:
                oben.append(p)
        for nummer, lf in self.cur.listen.items():
            listen[nummer] = ListFormat(eigenschaften(lf))
        modell.sections = schnitte_bilden(oben, marken, self._erste_seite)
        modell.lists = listen
        from lunivo_writer.adapter.qt.dokument import medien_sammeln
        modell.media = medien_sammeln(modell, self.doc)                    # frei positionierte Bilder: die Bilddaten wandern mit dem Modell
        return modell, self._erste_seite, meta, self.report


def lese_docx_modell(path: str):
    """→ ``(Document, PageSettings, meta, IOReport)`` oder ``None``, wenn das Dokument etwas enthält, das der Modell-Leser noch nicht kennt (dann ``docx_leser.read_docx`` nehmen).
    Wirft ``DocumentIOError`` wie ``read_docx``."""
    from lunivo_writer.dienste.import_grenzen import pruefe_paket
    pruefe_paket(path, "DOCX")
    docx_leser._schriften_ersatz()
    try:
        return _ModellReader(path).run_modell()
    except NichtImModell:
        return None
