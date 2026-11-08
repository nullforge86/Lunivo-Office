"""EditorWerkzeuge: fachlich abgegrenzte Editor-Funktionen."""
from __future__ import annotations

from __future__ import annotations  # noqa: F401
from PySide6.QtCore import QTimer, Qt, QUrl  # noqa: F401
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QPen, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat, QTextFrameFormat, QTextImageFormat, QTextListFormat, QTextTableFormat, QTextLength  # noqa: F401
from lunivo_writer.services.docx_reader import LH_PROPORTIONAL, STYLE_PROP  # noqa: F401
from lunivo_writer.editor.dokument.zusatz import P_VERSTECKT  # noqa: F401
from lunivo_writer.models.page import mm_to_px, px_to_mm  # noqa: F401
from lunivo_writer.editor.text import stile  # noqa: F401
from lunivo_writer.editor.dokument.zusatz import abstand_davor_px  # noqa: F401
from lunivo_writer.core.farben import Farbe  # noqa: F401


class EditorWerkzeugeMixin:
    """Teilbereich der Formatierungs- und Bearbeitungsfunktionen."""

    def insert_page_break(self) -> None:
        cur = self.textCursor()
        bf = QTextBlockFormat(); bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
        cur.insertBlock(bf)

    def insert_column_break(self) -> None:
        from lunivo_writer.editor.dokument.zusatz import B_SPALTE
        cur = self.textCursor()
        bf = QTextBlockFormat(); bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore); bf.setProperty(B_SPALTE, 1)
        cur.insertBlock(bf)

    def insert_table(self, rows: int, cols: int, borders: bool = True, spaltenbreite: float | None = None) -> None:
        """Tabelle an der Schreibmarke; ``spaltenbreite`` (Bildpunkte): feste Spalten, sonst passt sie sich der Seitenbreite an."""
        tf = QTextTableFormat()
        tf.setCellPadding(4); tf.setCellSpacing(0)
        tf.setBorder(1 if borders else 0); tf.setBorderCollapse(True)
        tf.setBorderBrush(QColor('#333333')); tf.setBorderStyle(QTextFrameFormat.BorderStyle_Solid)
        if spaltenbreite:
            tf.setColumnWidthConstraints([QTextLength(QTextLength.FixedLength, spaltenbreite)] * cols)
        else:
            tf.setWidth(QTextLength(QTextLength.PercentageLength, 100))
        t = self.textCursor().insertTable(rows, cols, tf)
        self.setTextCursor(t.cellAt(0, 0).firstCursorPosition())

    def insert_image(self, path: str) -> bool:
        img = QImage(path)
        if img.isNull():
            return False
        from lunivo_writer.editor.objekte import frei_objekt as FO
        FO.bild_einfuegen(self, img, float(img.width()), float(img.height()))        # freies Bild: Rahmen, Griffe, Schnellleiste
        return True

    def insert_link(self, url: str, text: str | None = None, tipp: str = "") -> None:
        """Link an der Schreibmarke; mit Markierung wird sie zum Link. ``tipp``: QuickInfo beim Überfahren."""
        cur = self.textCursor()
        f = QTextCharFormat()
        f.setAnchor(True); f.setAnchorHref(url)
        if tipp:
            f.setToolTip(tipp)
        f.setForeground(QBrush(QColor("#0563C1"))); f.setFontUnderline(True)
        if cur.hasSelection():
            cur.mergeCharFormat(f)
        else:
            cur.insertText(text or url, f)


    # ---- Suchen/Ersetzen ---------------------------------------------------------------

    def find_text(self, text: str, backwards=False, case=False, whole=False) -> bool:
        if not text:
            return False
        flags = QTextDocument.FindFlag(0)
        if backwards:
            flags |= QTextDocument.FindBackward
        if case:
            flags |= QTextDocument.FindCaseSensitively
        if whole:
            flags |= QTextDocument.FindWholeWords
        if self.find(text, flags):
            return True
        # Umbruch am Dokumentende/-anfang
        cur = self.textCursor()
        cur.movePosition(QTextCursor.End if backwards else QTextCursor.Start)
        self.setTextCursor(cur)
        return self.find(text, flags)

    def replace_current(self, find: str, repl: str, case=False) -> bool:
        cur = self.textCursor()
        sel = cur.selectedText()
        if cur.hasSelection() and (sel == find or (not case and sel.lower() == find.lower())):
            fmt = QTextCharFormat(self._format_am_anfang(cur))              # die Formatierung des ersetzten Textes bleibt (Schrift, fett, kursiv …)
            cur.insertText(repl, fmt)
            return True
        return False

    @staticmethod
    def _format_am_anfang(cur: QTextCursor) -> QTextCharFormat:
        """Das Zeichenformat des ersten Zeichens der Markierung (``charFormat()`` eines Cursors mit Markierung wäre das davor)."""
        c = QTextCursor(cur)
        c.setPosition(cur.selectionStart())
        c.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
        return c.charFormat()

    def replace_all(self, find: str, repl: str, case=False, whole=False) -> int:
        if not find:
            return 0
        flags = QTextDocument.FindFlag(0)
        if case:
            flags |= QTextDocument.FindCaseSensitively
        if whole:
            flags |= QTextDocument.FindWholeWords
        doc = self.document()
        cur = QTextCursor(doc)
        cur.beginEditBlock()
        n = 0
        pos = 0
        while True:
            found = doc.find(find, pos, flags)
            if found.isNull():
                break
            found.insertText(repl, QTextCharFormat(self._format_am_anfang(found)))
            pos = found.position()
            n += 1
        cur.endEditBlock()
        return n
