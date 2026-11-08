"""Absatzformat: fachlich abgegrenzte Editor-Funktionen."""
from __future__ import annotations

from __future__ import annotations  # noqa: F401
from PySide6.QtCore import QTimer, Qt, QUrl  # noqa: F401
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QPen, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat, QTextFrameFormat, QTextImageFormat, QTextListFormat, QTextTableFormat, QTextLength  # noqa: F401
from lunivo_writer.services.docx_reader import LH_PROPORTIONAL, STYLE_PROP  # noqa: F401
from lunivo_writer.editor.zusatz import P_VERSTECKT  # noqa: F401
from lunivo_writer.models.page import mm_to_px, px_to_mm  # noqa: F401
from lunivo_writer.editor import stile  # noqa: F401
from lunivo_writer.editor.zusatz import abstand_davor_px  # noqa: F401
from lunivo_writer.core.farben import Farbe  # noqa: F401


class AbsatzformatMixin:
    """Teilbereich der Formatierungs- und Bearbeitungsfunktionen."""

    def _block_merge(self, fn) -> None:
        cur = self.textCursor()
        cur.beginEditBlock()
        start, end = sorted((cur.anchor(), cur.position()))
        c = QTextCursor(self.document()); c.setPosition(start)
        blk = c.block()
        while blk.isValid() and blk.position() <= end:
            cc = QTextCursor(blk)
            bf = cc.blockFormat()
            fn(bf)
            cc.setBlockFormat(bf)
            blk = blk.next()
        cur.endEditBlock()

    def set_alignment(self, al: Qt.AlignmentFlag) -> None:
        kf = self._kf()
        if kf is not None:
            kf.ausrichtung_vom_werkzeug(al); self._kf_fertig(kf)
            return
        def f(bf):
            bf.setAlignment(al)
            if (al & Qt.AlignHCenter) and self.opt("schreibhilfe/akZentriert", True):
                bf.setTextIndent(0)               # „Bei zentriertem Ausrichten Erstzeileneinzug löschen“
        self._block_merge(f)

    def change_indent(self, delta_mm: float) -> None:
        d = mm_to_px(delta_mm)
        self._block_merge(lambda bf: bf.setLeftMargin(max(0.0, bf.leftMargin() + d)))

    def set_page_break_before(self, an: bool) -> None:
        from lunivo_writer.editor.zusatz import B_AUTOUMBRUCH

        def f(bf):
            bf.clearProperty(B_AUTOUMBRUCH)                 # ein selbst gesetzter Umbruch ersetzt einen, den Lunivo eingefügt hatte
            bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore if an else QTextFormat.PageBreak_Auto)
        self._block_merge(f)

    def set_indents(self, left_mm: float, right_mm: float, first_mm: float) -> None:
        def f(bf):
            from lunivo_writer.editor.querblatt import rechts_setzen
            bf.setLeftMargin(mm_to_px(left_mm)); rechts_setzen(bf, mm_to_px(right_mm))
            bf.setTextIndent(mm_to_px(first_mm))
        self._block_merge(f)

    def standard_tab_mm(self) -> float:
        """Standardtabstopps des Dokuments (Abstand in mm)."""
        return round(px_to_mm(self.document().defaultTextOption().tabStopDistance()), 2)

    def set_standard_tab_mm(self, mm: float) -> None:
        if mm <= 0:
            return
        opt = self.document().defaultTextOption()
        opt.setTabStopDistance(mm_to_px(mm))
        self.document().setDefaultTextOption(opt)
        self.document().setModified(True)
        self.viewport().update()

    def set_absatzopt(self, w: dict) -> None:
        """Absatzoptionen (Umbruchregeln, Zeilenumbruch, Zeichenabstand, Raster) der markierten Absätze setzen."""
        from lunivo_writer.editor import absatzopt
        self._block_merge(lambda bf: absatzopt.setzen(bf, w))

    def set_tabstopps(self, stopps) -> None:
        """Tabstopps als Liste aus (Millimeter, Ausrichtung, Füllzeichen) setzen."""
        from lunivo_writer.ui.baukasten.dokument.tabstopp_dialog import zu_block
        self._block_merge(lambda bf: zu_block(bf, stopps))
        self.viewport().update()

    def set_line_spacing(self, factor: float) -> None:
        self._block_merge(lambda bf: bf.setLineHeight(factor * 100, LH_PROPORTIONAL))

    def set_line_height(self, art: str, wert: float) -> None:
        """Zeilenabstand: ``faktor`` (Vielfaches), ``mindestens`` oder ``genau`` (Punkt)."""
        if art == "faktor":
            self.set_line_spacing(wert); return
        typ = {"genau": 2, "mindestens": 3}[art]                 # QTextBlockFormat.FixedHeight / MinimumHeight
        self._block_merge(lambda bf: bf.setLineHeight(wert / 0.75, typ))

    def set_paragraph_spacing(self, before_pt: float, after_pt: float) -> None:
        def f(bf):
            bf.setTopMargin(before_pt / 0.75); bf.setBottomMargin(after_pt / 0.75)
        self._block_merge(f)

    def toggle_list(self, kind: str, style=None) -> None:
        cur = self.textCursor()
        style = style if style is not None else (
            QTextListFormat.ListDisc if kind == "bullet" else QTextListFormat.ListDecimal)
        lst = cur.currentList()
        if lst and lst.format().style() == style:
            cur.beginEditBlock()
            blk = cur.block()
            lst.remove(blk)
            bf = cur.blockFormat(); bf.setIndent(0); bf.setLeftMargin(0); cur.setBlockFormat(bf)
            cur.endEditBlock()
            return
        fmt = QTextListFormat(); fmt.setStyle(style); fmt.setIndent(1)
        cur.createList(fmt)

    def list_remove(self, nur_qt: bool = False) -> None:
        """Aufzählung/Nummerierung vom Absatz an der Schreibmarke (bzw. der Auswahl) nehmen."""
        if not nur_qt:
            self.set_mehrstufig(None)
        cur = self.textCursor()
        cur.beginEditBlock()
        von, bis = sorted((cur.anchor(), cur.position()))
        c = QTextCursor(self.document()); c.setPosition(von)
        blk = c.block()
        while blk.isValid() and blk.position() <= bis:
            lst = blk.textList()
            if lst:
                lst.remove(blk)
                cc = QTextCursor(blk); bf = cc.blockFormat(); bf.setIndent(0); bf.setLeftMargin(0); cc.setBlockFormat(bf)
            blk = blk.next()
        cur.endEditBlock()

    def list_level(self, delta: int) -> None:
        m = self._mehrstufig_am_zeiger()
        if m:                                                    # mehrstufige Liste: die Ebene der markierten Absätze ändern
            from lunivo_writer.editor import mehrstufig
            from lunivo_writer.editor.zusatz import B_MEHRSTUFIG

            def f(bf):
                w = mehrstufig.aus_block(bf.stringProperty(B_MEHRSTUFIG)) if bf.hasProperty(B_MEHRSTUFIG) else None
                if w:
                    n = max(1, min(mehrstufig.EBENEN, w[0] + delta))
                    bf.setProperty(B_MEHRSTUFIG, mehrstufig.block_wert(n, w[1]))
            self._block_merge(f); mehrstufig.einrichten_alle(self.document()); self.viewport().update()
            return
        cur = self.textCursor()
        lst = cur.currentList()
        if not lst:
            return
        fmt = lst.format()
        fmt.setIndent(max(1, min(9, fmt.indent() + delta)))
        lst.setFormat(fmt)

    def set_mehrstufig(self, defn, ebene_nr: int | None = None) -> None:
        """Die markierten Absätze in eine mehrstufige Liste setzen (``defn=None``: herausnehmen). Der Text rückt ein, die Nummer steht davor."""
        from lunivo_writer.editor import mehrstufig
        from lunivo_writer.editor.zusatz import B_MEHRSTUFIG

        def f(bf):
            alt = mehrstufig.aus_block(bf.stringProperty(B_MEHRSTUFIG)) if bf.hasProperty(B_MEHRSTUFIG) else None
            if defn is None:
                if alt:
                    bf.clearProperty(B_MEHRSTUFIG); bf.setLeftMargin(0); bf.setTextIndent(0)
                return
            n = ebene_nr or (alt[0] if alt else 1)
            bf.setProperty(B_MEHRSTUFIG, mehrstufig.block_wert(n, defn))
        if defn is not None:
            self.list_remove(nur_qt=True)
        self._block_merge(f)
        mehrstufig.einrichten_alle(self.document())
        self.viewport().update()

    def set_liste(self, spec) -> None:
        """Liste setzen: ändert die Liste des Absatzes (alle ihre Absätze) oder legt für die Auswahl eine neue an; None nimmt sie weg."""
        from lunivo_writer.editor import listen
        if spec is None:
            self.list_remove(); return
        if "ebenen" in spec:
            self.set_mehrstufig(spec); return
        if spec.get("pos"):                              # eigene Position der Nummer: Lunivo zeichnet sie selbst (wie bei der Gliederung)
            from lunivo_writer.editor import mehrstufig
            self.set_mehrstufig(mehrstufig.als_mehrstufig(spec)); return
        self.set_mehrstufig(None)
        cur = self.textCursor()
        lst = cur.currentList()
        if lst:
            lst.setFormat(listen.zu_format(spec, lst.format().indent()))
        else:
            lst = cur.createList(listen.zu_format(spec))
        self._nummern_zeichen(lst, spec.get("zeichen"))

    @staticmethod
    def _nummern_zeichen(lst, zeichen) -> None:
        """Schrift der Nummern: Qt zeichnet sie mit dem Zeichenformat des Absatzes."""
        if not zeichen:
            return
        from lunivo_writer.ui.baukasten.formatierung.text_format import zu_format
        for i in range(lst.count()):
            c = QTextCursor(lst.item(i))
            f = zu_format(zeichen)
            if not zeichen.get("farbe"):
                f.clearProperty(QTextFormat.ForegroundBrush)
            if not zeichen.get("groesse"):
                f.clearProperty(QTextFormat.FontPointSize)
            if not zeichen.get("schrift"):
                f.clearProperty(QTextFormat.FontFamilies)
            c.mergeBlockCharFormat(f)
