"""DOCX lesen: Tabellen (verbundene Zellen, Rahmen, Maße, Zeilenhöhen)."""
from __future__ import annotations

from lunivo_writer.dienste.docx_teile.lesen_gemeinsam import (  # noqa: F401
    qn,
    Table,
    Paragraph,
    QBrush,
    QColor,
    QTextCharFormat,
    QTextCursor,
    QTextFrameFormat,
    QTextLength,
    QTextTableFormat,
    mm_to_px,
    Farbe,
    Qt,
)


# Rahmenstil DOCX → Qt (alles andere: durchgezogen)
_RAND_STIL = {"dotted": QTextFrameFormat.BorderStyle_Dotted, "dashed": QTextFrameFormat.BorderStyle_Dashed,
              "dashSmallGap": QTextFrameFormat.BorderStyle_Dashed, "double": QTextFrameFormat.BorderStyle_Double}


def _px(tw: float) -> float:
    """Zwanzigstelpunkte → Bildpunkte."""
    return mm_to_px(tw / 1440 * 25.4)


class TabellenMixin:
    """DOCX lesen: Tabellen (verbundene Zellen, Rahmen, Maße, Zeilenhöhen)."""

    # ---- Tabellen ----------------------------------------------------
    @staticmethod
    def _zelle_format(qcell, cell) -> None:
        """Zellenschattierung (w:shd) und senkrechte Ausrichtung (w:vAlign) aus der DOCX-Zelle."""
        from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT as V
        cf = qcell.format().toTableCellFormat()
        geaendert = False
        shd = cell._tc.xpath("w:tcPr/w:shd")
        if shd and shd[0].get(qn("w:fill")) not in (None, "auto"):
            cf.setBackground(QBrush(QColor("#" + shd[0].get(qn("w:fill")))))
            geaendert = True
        va = cell.vertical_alignment
        if va in (V.CENTER, V.BOTTOM):
            cf.setVerticalAlignment(QTextCharFormat.AlignMiddle if va == V.CENTER else QTextCharFormat.AlignBottom)
            geaendert = True
        if TabellenMixin._zellrahmen(cf, cell._tc):
            geaendert = True
        if geaendert:
            qcell.setFormat(cf)

    @staticmethod
    def _zellrahmen(cf, tc) -> bool:
        """Rahmen je Seite der Zelle (w:tcBorders): Stärke aus w:sz (Achtelpunkt), Farbe, Art. Ein ausdrücklich fehlender Rahmen
        (nil/none) wird als 0 gesetzt. → True, wenn etwas gesetzt wurde."""
        kanten = tc.xpath("w:tcPr/w:tcBorders")
        if not kanten:
            return False
        geaendert = False
        for seite, setze_breite, setze_farbe, setze_art in (
                ("top", cf.setTopBorder, cf.setTopBorderBrush, cf.setTopBorderStyle),
                ("left", cf.setLeftBorder, cf.setLeftBorderBrush, cf.setLeftBorderStyle),
                ("bottom", cf.setBottomBorder, cf.setBottomBorderBrush, cf.setBottomBorderStyle),
                ("right", cf.setRightBorder, cf.setRightBorderBrush, cf.setRightBorderStyle)):
            el = kanten[0].find(qn("w:" + seite))
            if el is None:
                continue
            art = el.get(qn("w:val")) or "nil"
            if art in ("nil", "none"):
                setze_breite(0)
            else:
                try:
                    punkte = int(el.get(qn("w:sz")) or 4) / 8
                except ValueError:
                    punkte = 0.5
                setze_breite(max(0.5, punkte * 96 / 72))
                farbe = el.get(qn("w:color")) or "auto"
                setze_farbe(QColor("#" + farbe) if farbe != "auto" else QColor("#000000"))
                setze_art(QTextFrameFormat.BorderStyle_Solid)
            geaendert = True
        return geaendert

    def add_table(self, table: Table, cursor: QTextCursor | None = None):
        """Tabelle an der Schreibmarke einfügen; mit ``cursor`` in eine Zelle (verschachtelte Tabelle)."""
        rows, cols = len(table.rows), len(table.columns)
        if rows == 0 or cols == 0:
            return
        tf = QTextTableFormat()
        self._tabellenformat(tf, table, cols)
        verschachtelt = cursor is not None
        qt = (cursor or self.cur).insertTable(rows, cols, tf)
        placed = self._zellbereiche(table, rows, cols)
        kennung = pr_stil = table._tbl.tblPr.find(qn("w:tblStyle")) if table._tbl.tblPr is not None else None
        self._tabellen_stil = self._stile_id.get(kennung.get(qn("w:val"))) if kennung is not None else None
        for r0, c0, _r1, _c1, cell in placed.values():
            self._zelle_fuellen(qt, r0, c0, cell)
        self._tabellen_stil = None
        for r0, c0, r1, c1, _cell in placed.values():           # verbinden erst nach dem Befüllen: Text in einer schon verbundenen Zelle löscht deren Spannweite
            if r1 > r0 or c1 > c0:
                qt.mergeCells(r0, c0, r1 - r0 + 1, c1 - c0 + 1)
        for r0, c0, _r1, _c1, cell in placed.values():          # erst nach dem Inhalt: das Einfügen von Text setzt das Zellenformat zurück
            self._zelle_format(qt.cellAt(r0, c0), cell)
        self._innenkanten(qt, table, placed, rows, cols)
        self._innenabstand_oben_unten(qt, table, rows, cols)   # zuerst: die Mindesthöhe der Zeilen darf dabei nicht verloren gehen
        self._zeilenhoehen(qt, table)
        self._kopfzeilen(qt, table)
        if verschachtelt:
            return
        self._cursor_ans_ende()
        self.fresh = True
        self.last_list = None

    def _cursor_ans_ende(self) -> None:
        """Nach einer Tabelle weiterschreiben: am Ende des Dokuments (der Modell-Leser überschreibt das; seine Schreibmarke steht schon im Block nach der Tabelle)."""
        self.cur = QTextCursor(self.doc)
        self.cur.movePosition(QTextCursor.End)

    @staticmethod
    def _zellbereiche(table: Table, rows: int, cols: int) -> dict:
        """Zellen mit Rechteck: {id: [Zeile0, Spalte0, Zeile1, Spalte1, Zelle]}. Jede Zeile wird nach ihren eigenen Spannweiten (gridSpan)
        gelegt; eine Zeile mit weniger Gitterspalten als die Tabelle lässt den Rest leer. Vertikal verbundene Zellen (vMerge) gehören
        zur Zelle darüber."""
        from docx.oxml.simpletypes import ST_Merge
        from docx.table import _Cell
        belegt: list[list] = [[None] * cols for _ in range(rows)]
        for r, tr in enumerate(table._tbl.tr_lst[:rows]):
            c = 0
            for tc in tr.tc_lst:
                span = max(1, tc.grid_span)
                if c >= cols:
                    break
                hat_text = any((t.text or "").strip() for t in tc.iter(qn("w:t")))
                if tc.vMerge == ST_Merge.CONTINUE and not hat_text and r > 0 and belegt[r - 1][c] is not None:
                    ziel = belegt[r - 1][c]                    # Fortsetzung ohne eigenen Text: zur Zelle darüber
                else:
                    ziel = tc
                for k in range(c, min(cols, c + span)):
                    belegt[r][k] = ziel
                c += span
        placed: dict[int, list] = {}
        for r in range(rows):
            for c in range(cols):
                tc = belegt[r][c]
                if tc is None:
                    continue
                e = placed.setdefault(id(tc), [r, c, r, c, _Cell(tc, table)])
                e[2] = max(e[2], r)
                e[3] = max(e[3], c)
        return placed

    def _zelle_fuellen(self, qt, r0: int, c0: int, cell) -> None:
        """Absätze der Zelle in die Qt-Zelle schreiben; verschachtelte Tabellen werden gemeldet, nicht dargestellt."""
        ccur = qt.cellAt(r0, c0).firstCursorPosition()
        first = True
        for item in cell.iter_inner_content():
            if isinstance(item, Paragraph):
                self.add_paragraph(item, ccur, reuse=first, in_table=True)
                first = False
            elif isinstance(item, Table):                    # verschachtelte Tabelle: in die Zelle setzen, danach geht der Text darunter weiter
                self.add_table(item, cursor=ccur)
                ccur = self._zelle_ende(qt, r0, c0)
                ccur.insertBlock()
                first = False

    @staticmethod
    def _zelle_ende(qt, r0: int, c0: int):
        """Schreibmarke am Ende der Zelle."""
        return QTextCursor(qt.cellAt(r0, c0).lastCursorPosition())

    def _innenabstand_oben_unten(self, qt, table: Table, rows: int, cols: int) -> None:
        """Oben und unten: der Innenabstand aus w:tblCellMar, sonst 0 — wie Word. Qt setzt sonst den seitlichen Wert auch oben und unten."""
        mar = {k: self._tw_von(table._tbl.tblPr, f"w:tblCellMar/w:{k}") for k in ("top", "bottom")}
        oben = _px(mar["top"][1]) if mar["top"] and mar["top"][0] == "dxa" else 0.0
        unten = _px(mar["bottom"][1]) if mar["bottom"] and mar["bottom"][0] == "dxa" else 0.0
        for r in range(rows):
            for c in range(cols):
                zelle = qt.cellAt(r, c)
                if not zelle.isValid():
                    continue
                cf = zelle.format().toTableCellFormat()
                cf.setTopPadding(oben); cf.setBottomPadding(unten)
                zelle.setFormat(cf)

    @staticmethod
    def _kopfzeilen(qt, table: Table) -> None:
        """Aufeinanderfolgende Kopfzeilen (w:tblHeader) ab der ersten Zeile."""
        kopf = 0
        for row in table.rows:
            if not row._tr.xpath("w:trPr/w:tblHeader"):
                break
            kopf += 1
        if kopf:
            f = qt.format(); f.setHeaderRowCount(kopf); qt.setFormat(f)

    @staticmethod
    def _tw(el):
        """(Art, Wert) eines Maßelements (w:tblW, w:tcW, w:tblCellMar-Kante …); Art ``dxa``/``pct``/``auto``, Wert in Zwanzigstelpunkten bzw. Prozent."""
        if el is None:
            return None
        art = el.get(qn("w:type")) or "dxa"
        roh = el.get(qn("w:w"))
        try:
            if roh is not None and roh.endswith("%"):
                return "pct", float(roh[:-1])
            wert = float(roh)
        except (TypeError, ValueError):
            return None
        if art == "pct":
            return "pct", wert / 50.0
        return ("auto" if art in ("auto", "nil") else "dxa"), wert

    def _tabellenformat(self, tf, table, cols: int) -> None:
        """Tabellenbreite, Ausrichtung, Zellabstand, Rahmen (Stärke, Farbe, Stil), Innenabstand und Spaltenbreiten aus w:tblPr/w:tblGrid/w:tcW.
        Vorgaben (100 %, Innenabstand 4, Rahmen #333333) gelten nur, wenn die Datei nichts angibt."""
        pr = table._tbl.tblPr
        self._tf_breite(tf, pr)
        jc = pr.xpath("w:jc/@w:val")
        if jc and jc[0] in ("center", "right", "end"):
            tf.setAlignment(Qt.AlignHCenter if jc[0] == "center" else Qt.AlignRight)
        self._tf_abstaende(tf, pr)
        tf.setBorderCollapse(True)
        self._tf_rahmen(tf, pr, table)
        self._tf_spalten(tf, table, cols)
        self._tf_schwebend(tf, pr)

    @staticmethod
    def _tf_schwebend(tf, pr) -> None:
        """Schwebende Tabelle (w:tblpPr): Qt legt den Text um einen links oder rechts schwebenden Rahmen, wie Word es tut.
        Abstände zum Text (leftFromText …) in Zwanzigstelpunkt → Bildpunkte."""
        lage = pr.find(qn("w:tblpPr"))
        if lage is None:
            return
        from PySide6.QtGui import QTextFrameFormat
        rechts = (lage.get(qn("w:tblpXSpec")) or "").lower() in ("right", "outside")
        tf.setPosition(QTextFrameFormat.FloatRight if rechts else QTextFrameFormat.FloatLeft)
        def px(name: str):
            v = lage.get(qn(name))
            return float(v) / 15.0 if v and v.lstrip("-").isdigit() else None
        for name, setze in (("w:leftFromText", tf.setLeftMargin), ("w:rightFromText", tf.setRightMargin),
                            ("w:topFromText", tf.setTopMargin), ("w:bottomFromText", tf.setBottomMargin)):
            wert = px(name)
            if wert is not None:
                setze(wert)

    def _tw_von(self, pr, pfad: str):
        """(Art, Wert) des ersten Elements am Pfad unter w:tblPr, sonst None."""
        el = pr.xpath(pfad)
        return self._tw(el[0] if el else None)

    def _tf_breite(self, tf, pr) -> None:
        w = self._tw_von(pr, "w:tblW")
        if w is None:
            tf.setWidth(QTextLength(QTextLength.PercentageLength, 100))
        elif w[0] == "pct" and w[1] > 0:
            tf.setWidth(QTextLength(QTextLength.PercentageLength, w[1]))
        elif w[0] == "dxa" and w[1] > 0:
            tf.setWidth(QTextLength(QTextLength.FixedLength, _px(w[1])))
        # Art "auto": Breite nach den Spalten (Qt: nicht gesetzt)

    def _tf_abstaende(self, tf, pr) -> None:
        """Innenabstand der Zellen (aus den Kanten) und Zellabstand."""
        mar = {k: self._tw_von(pr, f"w:tblCellMar/w:{k}") for k in ("left", "right", "top", "bottom")}
        gelesen = [m[1] for k in ("left", "right", "top", "bottom") if (m := mar[k]) and m[0] == "dxa"]
        tf.setCellPadding(_px(max(gelesen[:2] or gelesen)) if gelesen else 4)
        ab = self._tw_von(pr, "w:tblCellSpacing")
        tf.setCellSpacing(_px(ab[1]) if ab and ab[0] == "dxa" else 0)

    def _tf_rahmen(self, tf, pr, table) -> None:
        """Rahmen: Stärke, Farbe und Stil der ersten sichtbaren Kante; ohne w:tblBorders nur bei Tabellenstilen mit „Grid“."""
        kanten = pr.xpath("w:tblBorders")
        farbe, stil, breite = "#333333", QTextFrameFormat.BorderStyle_Solid, 1
        if kanten:
            ein = [k for k in kanten[0] if k.get(qn("w:val")) not in (None, "nil", "none")]
            if ein:
                farbe, stil, breite = self._kantenformat(ein[0], farbe)
            tf.setBorder(breite if ein else 0)
        else:
            tf.setBorder(1 if table.style is not None and "Grid" in (table.style.name or "") else 0)
        tf.setBorderBrush(QColor(farbe)); tf.setBorderStyle(stil)

    def _innenkanten(self, qt, table, placed: dict, rows: int, cols: int) -> None:
        """Innenlinien der Tabelle (w:insideH, w:insideV) und die Außenkanten (w:top …) als Rahmen je Zelle setzen, wenn die Zelle
        für diese Seite keine eigene Angabe hat (w:tcBorders). Formularfelder mit Unterstrich sind so gemacht."""
        grenzen = table._tbl.tblPr.find(qn("w:tblBorders")) if table._tbl.tblPr is not None else None
        if grenzen is None:
            return

        def kante(name: str):
            k = grenzen.find(qn("w:" + name))
            if k is None or k.get(qn("w:val")) in (None, "nil", "none"):
                return None
            return k

        kanten = {"top": kante("top"), "bottom": kante("bottom"), "left": kante("left"), "right": kante("right"),
                  "insideH": kante("insideH"), "insideV": kante("insideV")}
        for r0, c0, r1, c1, cell in placed.values():
            tc = cell._tc
            eigen = tc.xpath("w:tcPr/w:tcBorders")
            eigen = eigen[0] if eigen else None
            zelle = qt.cellAt(r0, c0)
            cf = zelle.format().toTableCellFormat()
            aendern = False
            for seite, quelle in (
                    ("top", kanten["top"] if r0 == 0 else kanten["insideH"]),
                    ("bottom", kanten["bottom"] if r1 == rows - 1 else kanten["insideH"]),
                    ("left", kanten["left"] if c0 == 0 else kanten["insideV"]),
                    ("right", kanten["right"] if c1 == cols - 1 else kanten["insideV"])):
                if eigen is not None and eigen.find(qn("w:" + seite)) is not None:
                    continue                                    # die Zelle hat ihre eigene Angabe für diese Seite
                if quelle is None:
                    continue
                breite, farbe, stil = self._kantenmasse(quelle)
                getattr(cf, "set%sBorder" % seite.capitalize())(breite)
                getattr(cf, "set%sBorderBrush" % seite.capitalize())(QColor(farbe))
                getattr(cf, "set%sBorderStyle" % seite.capitalize())(stil)
                aendern = True
            if aendern:
                zelle.setFormat(cf)

    def _kantenmasse(self, k):
        farbe, stil, breite = self._kantenformat(k, "#000000")
        return breite, farbe, stil

    @staticmethod
    def _kantenformat(k, farbe: str):
        """(Farbe, Stil, Stärke) einer Rahmenkante; ohne Farbangabe bleibt ``farbe``."""
        farbe_roh = k.get(qn("w:color"))
        if farbe_roh and farbe_roh != "auto":
            farbe = "#" + farbe_roh
        stil = _RAND_STIL.get(k.get(qn("w:val")), QTextFrameFormat.BorderStyle_Solid)
        try:
            breite = max(1, int(round(int(k.get(qn("w:sz"))) / 6)))
        except (TypeError, ValueError):
            breite = 1
        return farbe, stil, breite

    def _tf_spalten(self, tf, table, cols: int) -> None:
        """Spaltenbreiten: je Spalte tcW der ersten ungeteilten Zelle; fehlt tcW in der Spalte ganz, gilt die Gitterbreite."""
        spalten, gefunden = self._spalten_tcw(table, cols)
        grid = [self._tw(g) for g in table._tbl.tblGrid.gridCol_lst]
        lang, echt = [], False
        for i in range(cols):
            a = spalten[i] if gefunden[i] else (grid[i] if i < len(grid) else None)
            laenge = self._spaltenlaenge(a)
            echt = echt or laenge is not None
            lang.append(laenge if laenge is not None else QTextLength())
        if echt:
            tf.setColumnWidthConstraints(lang)

    def _spalten_tcw(self, table, cols: int):
        """Je Spalte das Breitenmaß (w:tcW) der ersten ungeteilten Zelle → (Maße, gefunden)."""
        spalten: list = [None] * cols
        gefunden = [False] * cols
        for tr in table._tbl.tr_lst:
            i = 0
            for tc in tr.tc_lst:
                span = max(1, tc.grid_span)
                if span == 1 and i < cols and not gefunden[i]:
                    el = tc.tcPr.tcW if tc.tcPr is not None else None
                    if el is not None:
                        spalten[i] = self._tw(el)
                        gefunden[i] = True
                i += span
        return spalten, gefunden

    @staticmethod
    def _spaltenlaenge(a):
        """Qt-Länge aus (Art, Wert): dxa → fest, pct → Prozent; sonst None."""
        if a and a[0] == "dxa" and a[1] > 0:
            return QTextLength(QTextLength.FixedLength, _px(a[1]))
        if a and a[0] == "pct" and a[1] > 0:
            return QTextLength(QTextLength.PercentageLength, a[1])
        return None

    def _zeilenhoehen(self, qt, table) -> None:
        """w:trHeight je Zeile als Mindesthöhe übernehmen (wie der Befehl „Zeilenhöhe“: Eigenschaft plus Innenabstand)."""
        from PySide6.QtGui import QFontMetricsF
        from lunivo_writer.editor.tabelle.tabelleneigenschaften import zeilenhoehe_setzen
        from lunivo_writer.modelle.seite import mm_to_px
        from PySide6.QtGui import QTextFrameFormat
        if qt.frameFormat().position() != QTextFrameFormat.InFlow:       # schwebende Tabelle (w:tblpPr): Qt stürzt beim Layout des halbfertigen Dokuments ab
            return
        lay = self.doc.documentLayout()
        lay.documentSize()                                   # Layout jetzt setzen: vorher liefert blockBoundingRect 0
        for r, row in enumerate(table.rows):
            h = row._tr.xpath("w:trPr/w:trHeight/@w:val")
            try:
                tw = float(h[0]) if h else 0.0
            except ValueError:
                continue
            if tw > 0:
                # Höhe des tatsächlichen Zellinhalts (nicht der Standardschrift): sonst bleibt die Zeile um den Unterschied zu niedrig
                zelle = qt.cellAt(r, 0)
                inhalt = 0.0
                if zelle.isValid():
                    b = zelle.begin()
                    while not b.atEnd():
                        blk = b.currentBlock()
                        if blk.isValid():
                            inhalt += lay.blockBoundingRect(blk).height()
                        b += 1
                zeilenhoehe_setzen(qt, r, mm_to_px(tw / 1440 * 25.4), inhalt or QFontMetricsF(self.doc.defaultFont()).lineSpacing())
