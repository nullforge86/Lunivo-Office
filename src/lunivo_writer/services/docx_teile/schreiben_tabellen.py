"""DOCX schreiben: Tabellen (Zellen, Rahmen, Maße)."""
from __future__ import annotations

from lunivo_writer.services.docx_teile.schreiben_gemeinsam import (  # noqa: F401
    OxmlElement,
    qn,
    Qt,
    QTextCharFormat,
    QTextTable,
    _Body,
    _CellBox,
)


class TabellenSchreiber:
    """DOCX schreiben: Tabellen (Zellen, Rahmen, Maße)."""

    # ---- Tabellen -------------------------------------------------------
    def write_table(self, qt: QTextTable, container):
        rows, cols = qt.rows(), qt.columns()
        t = container.add_table(rows, cols)
        if qt.format().border() > 0:
            t.style = self.d.styles["Table Grid"]
        done = set()
        for r in range(rows):
            self._zeilenhoehe(t.rows[r], qt, r)
            for c in range(cols):
                cell = qt.cellAt(r, c)
                key = (cell.row(), cell.column())
                if key in done:
                    continue
                done.add(key)
                rs, cs = cell.rowSpan(), cell.columnSpan()
                dcell = t.cell(r, c)
                if rs > 1 or cs > 1:
                    dcell = dcell.merge(t.cell(r + rs - 1, c + cs - 1))
                self._zelle_format(dcell, cell.format().toTableCellFormat())
                box = _CellBox(dcell)
                # Zelleninhalt: Rahmen der Zelle durchlaufen
                cit = cell.begin()
                first = True
                while not cit.atEnd():
                    blk = cit.currentBlock()
                    if blk.isValid():
                        para = box.first_paragraph() if first else box.add_paragraph()
                        first = False
                        self.write_block(blk, para)
                    cit += 1
        self._tabelle_eigenschaften(t, qt)
        if isinstance(container, _Body):
            pass

    def _tabelle_eigenschaften(self, t, qt: QTextTable) -> None:
        """Tabellenbreite, Ausrichtung, Zellabstand, Rahmen, Innenabstand (w:tblPr, in Schema-Reihenfolge), Spaltenbreiten
        (w:tblGrid, w:tcW) und Kopfzeile (w:tblHeader) der Qt-Tabelle schreiben."""
        from PySide6.QtGui import QTextLength
        from lunivo_writer.models.page import px_to_mm
        tw = lambda px: int(round(px_to_mm(px) / 25.4 * 1440))                # noqa: E731  Bildpunkte -> Zwanzigstelpunkte
        f = qt.format()
        inhalt = tw(self.page.content_width_px) if self.page is not None else 9000
        b = f.width()
        if b.type() == QTextLength.PercentageLength:
            breite, art, wert = inhalt * b.rawValue() / 100, "pct", int(round(b.rawValue() * 50))
        elif b.type() == QTextLength.FixedLength:
            breite = tw(b.rawValue()); art, wert = "dxa", int(breite)
        else:
            breite, art, wert = inhalt, "auto", 0
        pr = t._tbl.tblPr
        for tag in ("w:tblW", "w:jc", "w:tblCellSpacing", "w:tblBorders", "w:tblLayout", "w:tblCellMar"):
            for alt in pr.findall(qn(tag)):
                pr.remove(alt)
        neu = []

        def el(tag, **attr):
            e = OxmlElement(tag)
            for k, v in attr.items():
                e.set(qn("w:" + k), str(v))
            return e
        neu.append(el("w:tblW", type=art, w=wert))
        al = f.alignment()
        if al & Qt.AlignHCenter:
            neu.append(el("w:jc", val="center"))
        elif al & Qt.AlignRight:
            neu.append(el("w:jc", val="right"))
        if f.cellSpacing() > 0:
            neu.append(el("w:tblCellSpacing", w=tw(f.cellSpacing()), type="dxa"))
        if f.border() > 0:
            rb = el("w:tblBorders")
            val = self._RAND_VAL.get(f.borderStyle(), "single")
            for kante in ("top", "left", "bottom", "right", "insideH", "insideV"):
                rb.append(el("w:" + kante, val=val, sz=max(2, int(round(f.border() * 6))), space=0,
                             color=f.borderBrush().color().name()[1:].upper()))
            neu.append(rb)
        pad = tw(f.cellPadding())
        mar = el("w:tblCellMar")
        for kante in ("top", "left", "bottom", "right"):
            mar.append(el("w:" + kante, w=pad, type="dxa"))
        neu.append(mar)
        look = pr.find(qn("w:tblLook"))
        for e in neu:
            look.addprevious(e) if look is not None else pr.append(e)
        # Spalten: Fest -> dxa, Prozent -> pct, sonst auto (Gitterbreite aus dem Rest)
        lang = list(f.columnWidthConstraints())
        n = qt.columns()
        lang += [QTextLength()] * (n - len(lang))
        w = [0.0] * n
        for i, x in enumerate(lang[:n]):
            if x.type() == QTextLength.FixedLength:
                w[i] = float(tw(x.rawValue()))
            elif x.type() == QTextLength.PercentageLength:
                w[i] = breite * x.rawValue() / 100
        frei = [i for i in range(n) if w[i] == 0.0]
        if frei:
            rest = max(breite - sum(w), 120.0 * len(frei))
            for i in frei:
                w[i] = rest / len(frei)
        for g, x in zip(t._tbl.tblGrid.gridCol_lst, w):
            g.set(qn("w:w"), str(int(round(x))))
        for tr in t._tbl.tr_lst:
            i = 0
            for tc in tr.tc_lst:
                span = max(1, tc.grid_span)
                x = lang[i] if i < n else QTextLength()
                tcw = tc.get_or_add_tcPr().get_or_add_tcW()
                if span == 1 and x.type() == QTextLength.FixedLength:
                    tcw.set(qn("w:type"), "dxa"); tcw.set(qn("w:w"), str(int(round(w[i]))))
                elif span == 1 and x.type() == QTextLength.PercentageLength:
                    tcw.set(qn("w:type"), "pct"); tcw.set(qn("w:w"), str(int(round(x.rawValue() * 50))))
                elif span == 1:
                    tcw.set(qn("w:type"), "auto"); tcw.set(qn("w:w"), "0")
                else:
                    tcw.set(qn("w:type"), "dxa"); tcw.set(qn("w:w"), str(int(round(sum(w[i:i + span])))))
                i += span
        for r in range(min(f.headerRowCount(), len(t.rows))):
            t.rows[r]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))

    @staticmethod
    def _zeilenhoehe(drow, qt, r: int) -> None:
        """Mindesthöhe der Zeile (Z_MINHOEHE, Bildpunkte) als w:trHeight mit hRule=atLeast, in Zwanzigstelpunkten."""
        from lunivo_writer.editor.tabelle.tabelleneigenschaften import zeilenhoehe_lesen
        from lunivo_writer.models.page import px_to_mm
        px = zeilenhoehe_lesen(qt, r)
        if px > 0:
            h = OxmlElement("w:trHeight")
            h.set(qn("w:val"), str(int(round(px_to_mm(px) / 25.4 * 1440)))); h.set(qn("w:hRule"), "atLeast")
            drow._tr.get_or_add_trPr().append(h)

    @staticmethod
    def _zelle_format(dcell, cf) -> None:
        """Zellenschattierung (w:shd) und senkrechte Ausrichtung (w:vAlign) der Qt-Zelle übernehmen."""
        from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT as V
        br = cf.background()
        if br.style() != Qt.NoBrush and br.color().alpha() > 0:
            tcpr = dcell._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), br.color().name()[1:].upper())
            for alt in tcpr.findall(qn("w:shd")):
                tcpr.remove(alt)
            tcpr.append(shd)
        va = {QTextCharFormat.AlignMiddle: V.CENTER, QTextCharFormat.AlignBottom: V.BOTTOM}.get(cf.verticalAlignment())
        if va is not None:
            dcell.vertical_alignment = va
