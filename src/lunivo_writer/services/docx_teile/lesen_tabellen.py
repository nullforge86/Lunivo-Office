"""DOCX lesen: Tabellen (verbundene Zellen, Rahmen, Maße, Zeilenhöhen)."""
from __future__ import annotations

from lunivo_writer.services.docx_teile.lesen_gemeinsam import (  # noqa: F401
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
        if geaendert:
            qcell.setFormat(cf)

    def add_table(self, table: Table):
        rows, cols = len(table.rows), len(table.columns)
        if rows == 0 or cols == 0:
            return
        tf = QTextTableFormat()
        self._tabellenformat(tf, table, cols)
        qt = self.cur.insertTable(rows, cols, tf)

        # Zellen mit Rechteck: gleiche tc → eine Zelle
        placed: dict[int, list] = {}
        for r in range(rows):
            for c in range(cols):
                tc = table.cell(r, c)._tc
                e = placed.setdefault(id(tc), [r, c, r, c, table.cell(r, c)])
                e[2] = max(e[2], r)
                e[3] = max(e[3], c)
        for r0, c0, _r1, _c1, cell in placed.values():
            ccur = qt.cellAt(r0, c0).firstCursorPosition()
            first = True
            for item in cell.iter_inner_content():
                if isinstance(item, Paragraph):
                    self.add_paragraph(item, ccur, reuse=first, in_table=True)
                    first = False
                else:
                    self.report.warn("Verschachtelte Tabellen werden nicht dargestellt.")
        for r0, c0, r1, c1, _cell in placed.values():           # verbinden erst nach dem Befüllen: Text in einer schon verbundenen Zelle löscht deren Spannweite
            if r1 > r0 or c1 > c0:
                qt.mergeCells(r0, c0, r1 - r0 + 1, c1 - c0 + 1)
        for r0, c0, _r1, _c1, cell in placed.values():          # erst nach dem Inhalt: das Einfügen von Text setzt das Zellenformat zurück
            self._zelle_format(qt.cellAt(r0, c0), cell)
        self._zeilenhoehen(qt, table)
        kopf = 0
        for row in table.rows:
            if not row._tr.xpath("w:trPr/w:tblHeader"):
                break
            kopf += 1
        if kopf:
            f = qt.format(); f.setHeaderRowCount(kopf); qt.setFormat(f)
        self.cur = QTextCursor(self.doc)
        self.cur.movePosition(QTextCursor.End)
        self.fresh = True
        self.last_list = None

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
        px = lambda tw: mm_to_px(tw / 1440 * 25.4)                              # noqa: E731
        pr = table._tbl.tblPr
        x = pr.xpath
        w = self._tw(x("w:tblW")[0] if x("w:tblW") else None)
        if w is None:
            tf.setWidth(QTextLength(QTextLength.PercentageLength, 100))
        elif w[0] == "pct" and w[1] > 0:
            tf.setWidth(QTextLength(QTextLength.PercentageLength, w[1]))
        elif w[0] == "dxa" and w[1] > 0:
            tf.setWidth(QTextLength(QTextLength.FixedLength, px(w[1])))
        # Art "auto": Breite nach den Spalten (Qt: nicht gesetzt)
        jc = x("w:jc/@w:val")
        if jc and jc[0] in ("center", "right", "end"):
            tf.setAlignment(Qt.AlignHCenter if jc[0] == "center" else Qt.AlignRight)
        mar = {k: self._tw(x(f"w:tblCellMar/w:{k}")[0] if x(f"w:tblCellMar/w:{k}") else None) for k in ("left", "right", "top", "bottom")}
        gelesen = [m[1] for k in ("left", "right", "top", "bottom") if (m := mar[k]) and m[0] == "dxa"]
        tf.setCellPadding(px(max(gelesen[:2] or gelesen)) if gelesen else 4)
        ab = self._tw(x("w:tblCellSpacing")[0] if x("w:tblCellSpacing") else None)
        tf.setCellSpacing(px(ab[1]) if ab and ab[0] == "dxa" else 0)
        tf.setBorderCollapse(True)
        kanten = x("w:tblBorders")
        farbe, stil, breite = "#333333", QTextFrameFormat.BorderStyle_Solid, 1
        if kanten:
            ein = [k for k in kanten[0] if k.get(qn("w:val")) not in (None, "nil", "none")]
            if ein:
                k = ein[0]
                farbe_roh = k.get(qn("w:color"))
                if farbe_roh and farbe_roh != "auto":
                    farbe = "#" + farbe_roh
                stil = {"dotted": QTextFrameFormat.BorderStyle_Dotted, "dashed": QTextFrameFormat.BorderStyle_Dashed,
                        "dashSmallGap": QTextFrameFormat.BorderStyle_Dashed, "double": QTextFrameFormat.BorderStyle_Double
                        }.get(k.get(qn("w:val")), QTextFrameFormat.BorderStyle_Solid)
                try:
                    breite = max(1, int(round(int(k.get(qn("w:sz"))) / 6)))
                except (TypeError, ValueError):
                    breite = 1
            tf.setBorder(breite if ein else 0)
        else:
            tf.setBorder(1 if table.style is not None and "Grid" in (table.style.name or "") else 0)
        tf.setBorderBrush(QColor(farbe)); tf.setBorderStyle(stil)
        # Spaltenbreiten: je Spalte tcW der ersten ungeteilten Zelle; fehlt tcW in der Spalte ganz, gilt die Gitterbreite
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
        grid = [self._tw(g) for g in table._tbl.tblGrid.gridCol_lst]
        lang, echt = [], False
        for i in range(cols):
            a = spalten[i] if gefunden[i] else (grid[i] if i < len(grid) else None)
            if a and a[0] == "dxa" and a[1] > 0:
                lang.append(QTextLength(QTextLength.FixedLength, px(a[1]))); echt = True
            elif a and a[0] == "pct" and a[1] > 0:
                lang.append(QTextLength(QTextLength.PercentageLength, a[1])); echt = True
            else:
                lang.append(QTextLength())
        if echt:
            tf.setColumnWidthConstraints(lang)

    def _zeilenhoehen(self, qt, table) -> None:
        """w:trHeight je Zeile als Mindesthöhe übernehmen (wie der Befehl „Zeilenhöhe“: Eigenschaft plus Innenabstand)."""
        from PySide6.QtGui import QFontMetricsF
        from lunivo_writer.editor.tabelleneigenschaften import zeilenhoehe_setzen
        from lunivo_writer.models.page import mm_to_px
        zeile = QFontMetricsF(self.doc.defaultFont()).lineSpacing()
        for r, row in enumerate(table.rows):
            h = row._tr.xpath("w:trPr/w:trHeight/@w:val")
            try:
                tw = float(h[0]) if h else 0.0
            except ValueError:
                continue
            if tw > 0:
                zeilenhoehe_setzen(qt, r, mm_to_px(tw / 1440 * 25.4), zeile)
