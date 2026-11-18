"""DOCX schreiben: Tabellen (Zellen, Rahmen, Maße)."""
from __future__ import annotations

from PySide6.QtGui import QTextLength

from lunivo_writer.modelle.seite import px_to_mm
from lunivo_writer.dienste.docx_teile.schreiben_gemeinsam import (  # noqa: F401
    OxmlElement,
    qn,
    Qt,
    QTextCharFormat,
    QTextTable,
    umbruch,
    _Body,
    _CellBox,
)


def _verschachtelte_in_zelle(qt, cell) -> list:
    """Verschachtelte Tabellen, die in dieser Zelle der Tabelle ``qt`` stehen: [(Position, Tabelle)], in Dokumentreihenfolge."""
    if qt is None:
        return []
    aus = []
    for f in qt.childFrames():
        if not isinstance(f, QTextTable):
            continue
        zelle = qt.cellAt(f.firstPosition())
        if zelle.isValid() and zelle.row() == cell.row() and zelle.column() == cell.column():
            aus.append((f.firstPosition(), f))
    return sorted(aus, key=lambda x: x[0])


def _twips(px: float) -> int:
    """Bildpunkte → Zwanzigstelpunkte."""
    return int(round(px_to_mm(px) / 25.4 * 1440))


def _wel(tag: str, **attr):
    """DOCX-Element mit Attributen im Namensraum w."""
    e = OxmlElement(tag)
    for k, v in attr.items():
        e.set(qn("w:" + k), str(v))
    return e


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
                self._zelle_schreiben(t, cell, r, c, qt)
        self._tabelle_eigenschaften(t, qt)

    def _zelle_schreiben(self, t, cell, r: int, c: int, qt: QTextTable | None = None) -> None:
        """Eine Zelle (bei verbundenen Zellen den ganzen Bereich) mit Format und den Absätzen ihres Inhalts.
        Verschachtelte Tabellen dieser Zelle werden an ihrer Stelle als Tabelle in die Zelle geschrieben. Qt gibt sie beim Durchlauf
        der Zelle nicht aus (sie sind eigene Rahmen darin), deshalb kommen sie aus den Kindrahmen der Tabelle."""
        rs, cs = cell.rowSpan(), cell.columnSpan()
        dcell = t.cell(r, c)
        if rs > 1 or cs > 1:
            dcell = dcell.merge(t.cell(r + rs - 1, c + cs - 1))
        self._zelle_format(dcell, cell.format().toTableCellFormat())
        box = _CellBox(dcell)
        verschachtelt = _verschachtelte_in_zelle(qt, cell)
        cit = cell.begin()                                  # Zelleninhalt: Absätze der Zelle in ihrer Reihenfolge
        first = True

        nach_tabelle = False

        def tabelle_schreiben(inner):
            nonlocal first, nach_tabelle
            self.write_table(inner, box)
            first = False
            nach_tabelle = True

        while not cit.atEnd():
            blk = cit.currentBlock()
            if blk.isValid():
                while verschachtelt and verschachtelt[0][0] < blk.position():
                    tabelle_schreiben(verschachtelt.pop(0)[1])
                if first:
                    para = box.first_paragraph()
                elif nach_tabelle:
                    para = box.add_paragraph()                  # der Absatz nach der Tabelle ist der nächste Absatz des Zellinhalts
                else:
                    para = box.add_paragraph()
                nach_tabelle = False
                first = False
                self.write_block(blk, para)
            else:                                               # schwebendes Bild im Rahmen (Textumfluss): am nächsten Absatz der Zelle verankern
                fr = cit.currentFrame()
                if fr is not None and not isinstance(fr, QTextTable) and fr.frameFormat().position() in umbruch.SEITEN \
                        and umbruch.bild_im_rahmen(fr) is not None:
                    self._vorab_bilder.append((umbruch.bild_im_rahmen(fr), umbruch.SEITEN[fr.frameFormat().position()]))
            cit += 1
        while verschachtelt:
            tabelle_schreiben(verschachtelt.pop(0)[1])
        if nach_tabelle:
            box.add_paragraph()                                 # eine Zelle endet mit einem Absatz, nicht mit einer Tabelle

    def _tabelle_eigenschaften(self, t, qt: QTextTable) -> None:
        """Tabellenbreite, Ausrichtung, Zellabstand, Rahmen, Innenabstand (w:tblPr, in Schema-Reihenfolge), Spaltenbreiten
        (w:tblGrid, w:tcW) und Kopfzeile (w:tblHeader) der Qt-Tabelle schreiben."""
        f = qt.format()
        inhalt = _twips(self.page.content_width_px) if self.page is not None else 9000
        breite, art, wert = self._tabellenbreite(f, inhalt)
        pr = t._tbl.tblPr
        for tag in ("w:tblW", "w:jc", "w:tblCellSpacing", "w:tblBorders", "w:tblLayout", "w:tblCellMar"):
            for alt in pr.findall(qn(tag)):
                pr.remove(alt)
        look = pr.find(qn("w:tblLook"))
        for e in self._tblpr_elemente(f, art, wert):
            look.addprevious(e) if look is not None else pr.append(e)
        lang, w = self._spaltenbreiten(f, qt.columns(), breite)
        for g, x in zip(t._tbl.tblGrid.gridCol_lst, w):
            g.set(qn("w:w"), str(int(round(x))))
        self._zellbreiten(t, lang, w, qt.columns())
        for r in range(min(f.headerRowCount(), len(t.rows))):
            t.rows[r]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))

    @staticmethod
    def _tabellenbreite(f, inhalt: int):
        """Breite der Tabelle in Zwanzigstelpunkten → (Breite, Art pct/dxa/auto, Wert für w:tblW)."""
        b = f.width()
        if b.type() == QTextLength.PercentageLength:
            return inhalt * b.rawValue() / 100, "pct", int(round(b.rawValue() * 50))
        if b.type() == QTextLength.FixedLength:
            breite = _twips(b.rawValue())
            return breite, "dxa", int(breite)
        return inhalt, "auto", 0

    def _tblpr_elemente(self, f, art: str, wert: int) -> list:
        """Neue Kindelemente von w:tblPr in Schema-Reihenfolge: Breite, Ausrichtung, Zellabstand, Rahmen, Innenabstand."""
        neu = [_wel("w:tblW", type=art, w=wert)]
        al = f.alignment()
        if al & Qt.AlignHCenter:
            neu.append(_wel("w:jc", val="center"))
        elif al & Qt.AlignRight:
            neu.append(_wel("w:jc", val="right"))
        if f.cellSpacing() > 0:
            neu.append(_wel("w:tblCellSpacing", w=_twips(f.cellSpacing()), type="dxa"))
        if f.border() > 0:
            neu.append(self._tabellenrahmen(f))
        pad = _twips(f.cellPadding())
        mar = _wel("w:tblCellMar")
        for kante in ("top", "left", "bottom", "right"):
            mar.append(_wel("w:" + kante, w=pad, type="dxa"))
        neu.append(mar)
        return neu

    def _tabellenrahmen(self, f):
        rb = _wel("w:tblBorders")
        val = self._RAND_VAL.get(f.borderStyle(), "single")
        for kante in ("top", "left", "bottom", "right", "insideH", "insideV"):
            rb.append(_wel("w:" + kante, val=val, sz=max(2, int(round(f.border() * 6))), space=0,
                           color=f.borderBrush().color().name()[1:].upper()))
        return rb

    @staticmethod
    def _spaltenbreiten(f, n: int, breite: float):
        """Spalten: Fest -> dxa, Prozent -> pct, sonst auto (Gitterbreite aus dem Rest) → (Vorgaben, Gitterbreiten)."""
        lang = list(f.columnWidthConstraints())
        lang += [QTextLength()] * (n - len(lang))
        w = [0.0] * n
        for i, x in enumerate(lang[:n]):
            if x.type() == QTextLength.FixedLength:
                w[i] = float(_twips(x.rawValue()))
            elif x.type() == QTextLength.PercentageLength:
                w[i] = breite * x.rawValue() / 100
        frei = [i for i in range(n) if w[i] == 0.0]
        if frei:
            rest = max(breite - sum(w), 120.0 * len(frei))
            for i in frei:
                w[i] = rest / len(frei)
        return lang, w

    @staticmethod
    def _zellbreiten(t, lang: list, w: list, n: int) -> None:
        """w:tcW jeder Zelle: eigene Vorgabe bei einfacher Zelle, Summe der Gitterbreiten bei verbundenen."""
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

    @staticmethod
    def _zeilenhoehe(drow, qt, r: int) -> None:
        """Mindest- oder exakte Zeilenhöhe als w:trHeight in Zwanzigstelpunkten."""
        from lunivo_writer.editor.tabelle.tabelleneigenschaften import zeilenhoehe_lesen
        from lunivo_writer.core.layout.seitenumbruch import P_ZEILE_HOEHE_ART
        px = zeilenhoehe_lesen(qt, r)
        if px > 0:
            exakt = any(qt.cellAt(r, c).format().property(int(P_ZEILE_HOEHE_ART.split(":")[1])) == "exact"
                        for c in range(qt.columns()) if qt.cellAt(r, c).row() == r)
            h = OxmlElement("w:trHeight")
            h.set(qn("w:val"), str(_twips(px))); h.set(qn("w:hRule"), "exact" if exakt else "atLeast")
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
