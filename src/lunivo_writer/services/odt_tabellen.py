"""Tabellen aus ODT-Dokumenten in QTextDocument übernehmen."""
from __future__ import annotations

import xml.etree.ElementTree as ET

from PySide6.QtGui import QBrush, QColor, QTextFrameFormat, QTextLength, QTextTableFormat

from lunivo_writer.services.odt_xml import MAX_WIEDERHOLUNG, _q, _px

QTextFrameFormatBorder = QTextFrameFormat.BorderStyle_Solid


def tabelle(self, el: ET.Element, ort) -> None:
        breiten: list[float] = []
        zeilen: list[ET.Element] = []
    
        def sammeln(e: ET.Element) -> None:
            for k in e:
                if k.tag == _q("table:table-column"):
                    n = min(MAX_WIEDERHOLUNG, int(k.get(_q("table:number-columns-repeated"), "1") or 1))
                    b = _px(self.stile.eigenschaften("table-column", k.get(_q("table:style-name")), "table-column")
                            .get("style:column-width"))
                    breiten.extend([b] * n)
                elif k.tag == _q("table:table-row"):
                    n = min(MAX_WIEDERHOLUNG, int(k.get(_q("table:number-rows-repeated"), "1") or 1))
                    zeilen.extend([k] * n)
                elif k.tag in (_q("table:table-columns"), _q("table:table-header-columns"), _q("table:table-rows"),
                               _q("table:table-header-rows"), _q("table:table-column-group"), _q("table:table-row-group")):
                    sammeln(k)
        sammeln(el)
        zellen = []
        for z in zeilen:
            reihe = []
            for c in z:
                if c.tag in (_q("table:table-cell"), _q("table:covered-table-cell")):
                    n = min(MAX_WIEDERHOLUNG, int(c.get(_q("table:number-columns-repeated"), "1") or 1))
                    reihe.extend([c] * n)
            zellen.append(reihe)
        spalten = max([len(r) for r in zellen] + [len(breiten), 1])
        if not zeilen:
            return
        tf = QTextTableFormat()
        tf.setCellPadding(4)
        tf.setCellSpacing(0)
        tf.setBorder(1)
        tf.setBorderBrush(QBrush(QColor("#000000")))
        tf.setBorderStyle(QTextFrameFormatBorder)
        if breiten and len(breiten) == spalten and sum(breiten) > 0:
            tf.setColumnWidthConstraints([QTextLength(QTextLength.PercentageLength, 100 * b / sum(breiten)) for b in breiten])
        if not ort.frei:
            ort.cur.insertBlock()
        t = ort.cur.insertTable(len(zeilen), spalten, tf)
        for r, reihe in enumerate(zellen):
            for c, zelle in enumerate(reihe):
                if zelle.tag != _q("table:table-cell"):
                    continue
                zelle_ort = _Ort(t.cellAt(r, c).firstCursorPosition())
                hg = self.stile.eigenschaften("table-cell", zelle.get(_q("table:style-name")), "table-cell").get("fo:background-color")
                if hg and hg != "transparent" and QColor(hg).isValid():
                    zf = t.cellAt(r, c).format()
                    zf.setBackground(QBrush(QColor(hg)))
                    t.cellAt(r, c).setFormat(zf)
                self.bereich(list(zelle), zelle_ort)
                zs = int(zelle.get(_q("table:number-rows-spanned"), "1") or 1)
                ss = int(zelle.get(_q("table:number-columns-spanned"), "1") or 1)
                if zs > 1 or ss > 1:
                    t.mergeCells(r, c, min(zs, len(zeilen) - r), min(ss, spalten - c))
        ort.cur = QTextCursor(self.doc)
        ort.cur.setPosition(t.lastPosition() + 1)
        ort.frei = True
