"""Zeichenformat: fachlich abgegrenzte Editor-Funktionen."""
from __future__ import annotations

from __future__ import annotations  # noqa: F401
from PySide6.QtCore import QTimer, Qt, QUrl  # noqa: F401
from PySide6.QtGui import QBrush, QColor, QFont, QImage, QPen, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextFormat, QTextFrameFormat, QTextImageFormat, QTextListFormat, QTextTableFormat, QTextLength  # noqa: F401
from lunivo_writer.dienste.docx_leser import LH_PROPORTIONAL, STYLE_PROP  # noqa: F401
from lunivo_writer.editor.dokument.zusatz import P_VERSTECKT  # noqa: F401
from lunivo_writer.modelle.seite import mm_to_px, px_to_mm  # noqa: F401
from lunivo_writer.editor.text import stile  # noqa: F401
from lunivo_writer.editor.dokument.zusatz import abstand_davor_px  # noqa: F401
from lunivo_writer.kern.farben import Farbe  # noqa: F401


class ZeichenformatMixin:
    """Teilbereich der Formatierungs- und Bearbeitungsfunktionen."""

    def _kf(self):
        """Der Kopf-/Fußzeilen-Bearbeiter, solange die Schreibmarke dort steht (dann wirken die Start-Werkzeuge auf die Zeile), sonst None."""
        kf = getattr(self, "_kopffuss", None)
        return kf if kf is not None and kf.aktiv and kf.im_feld else None

    def _kf_fertig(self, kf) -> None:
        QTimer.singleShot(0, kf.feld.setFocus)                  # die Werkzeuge geben den Fokus an den Editor zurück: wieder ins Feld

    def _merge(self, fmt: QTextCharFormat) -> None:
        kf = self._kf()
        if kf is not None:
            kf.format_anwenden(fmt); self._kf_fertig(kf)
            return
        cur = self.textCursor()
        if not self.modell_spiegel().zeichenformat(cur, fmt):         # Auswahl: Oberfläche → Adapter → Kern → Ansicht; sonst (keine Auswahl, sehr großes Dokument) wie bisher
            cur.mergeCharFormat(fmt)
        self.mergeCurrentCharFormat(fmt)

    def text_ersetzen(self, cursor: QTextCursor, text: str, fmt: QTextCharFormat | None = None) -> None:
        """Die Auswahl des Cursors durch Text ersetzen (Rechtschreibkorrektur, Ersetzen, Autokorrektur): Oberfläche → Adapter → Kern → Ansicht; in sehr großen Dokumenten direkt am Textdokument."""
        sp = self.modell_spiegel()
        if sp.zu_gross():
            cursor.insertText(text, fmt) if fmt is not None else cursor.insertText(text)
            return
        sp.ersetzen(cursor, text, fmt)

    def modell_spiegel(self, modell=None):
        """Der Spiegel zwischen dem Textdokument des Editors und der Qt-freien Bearbeitungssitzung (``adapter/qt/bearbeitung.py``)."""
        from lunivo_writer.adapter.qt.bearbeitung import ModellSpiegel
        sp = self.__dict__.get("_modell_spiegel_obj")
        if sp is None or sp.qdoc is not self.document():
            sp = self.__dict__["_modell_spiegel_obj"] = ModellSpiegel(self.document(), getattr(self, "page", None), modell)
        elif modell is not None:
            sp.modell_vorbelegen(modell)
        return sp

    def toggle_bold(self, on: bool) -> None:
        f = QTextCharFormat(); f.setFontWeight(QFont.Bold if on else QFont.Normal); self._merge(f)

    def toggle_italic(self, on: bool) -> None:
        f = QTextCharFormat(); f.setFontItalic(on); self._merge(f)

    def toggle_underline(self, on: bool) -> None:
        f = QTextCharFormat(); f.setFontUnderline(on); self._merge(f)

    def set_underline_style(self, stil) -> None:
        f = QTextCharFormat()
        f.setUnderlineStyle(stil)
        self._merge(f)

    def set_outline(self, an: bool) -> None:
        f = QTextCharFormat()
        f.setTextOutline(QPen(QColor(Farbe.SCHWARZ)) if an else QPen(Qt.NoPen))
        self._merge(f)

    def set_letter_spacing(self, px: float) -> None:
        f = QTextCharFormat()
        f.setFontLetterSpacingType(QFont.AbsoluteSpacing)
        f.setFontLetterSpacing(px)
        self._merge(f)

    def set_capitalization(self, cap) -> None:
        f = QTextCharFormat()
        f.setFontCapitalization(cap)
        self._merge(f)

    def toggle_strike(self, on: bool) -> None:
        f = QTextCharFormat(); f.setFontStrikeOut(on); self._merge(f)

    def set_script(self, kind: str | None) -> None:
        f = QTextCharFormat()
        f.setVerticalAlignment({"sup": QTextCharFormat.AlignSuperScript,
                                "sub": QTextCharFormat.AlignSubScript}.get(kind, QTextCharFormat.AlignNormal))
        self._merge(f)

    def set_font_family(self, family: str) -> None:
        f = QTextCharFormat(); f.setFontFamilies([family]); self._merge(f)

    def set_font_size(self, pt: float) -> None:
        if pt > 0:
            f = QTextCharFormat(); f.setFontPointSize(pt); self._merge(f)

    def grow_font(self, delta: float) -> None:
        kf = self._kf()
        cur = self.textCursor()
        size = kf.format_lesen().fontPointSize() if kf is not None else cur.charFormat().fontPointSize()
        size = size or self.document().defaultFont().pointSizeF() or 11
        self.set_font_size(max(1.0, min(400.0, size + delta)))

    def set_text_color(self, color: QColor | None) -> None:
        f = QTextCharFormat()
        f.setForeground(QBrush(color) if color else QBrush(Qt.NoBrush))
        if color is None:
            f.clearProperty(QTextFormat.ForegroundBrush)
            kf = self._kf()
            if kf is not None:
                kf.format_anwenden(f, farbe_weg=True); self._kf_fertig(kf)
                return
        self._merge(f)

    def set_highlight(self, color: QColor | None) -> None:
        f = QTextCharFormat()
        if color:
            f.setBackground(QBrush(color))
        else:
            f.setBackground(QBrush(Qt.NoBrush))
        self._merge(f)

    def change_case(self, mode: str) -> None:
        cur = self.textCursor()
        if not cur.hasSelection():
            cur.select(QTextCursor.WordUnderCursor)
        txt = cur.selectedText()
        from lunivo_writer.editor.text.schreibweise import umwandeln
        new = umwandeln(txt, mode)
        if new != txt:
            cur.insertText(new)

    def clear_formatting(self) -> None:
        kf = self._kf()
        if kf is not None:
            kf.format_loeschen(); self._kf_fertig(kf)
            return
        cur = self.textCursor()
        if not cur.hasSelection():
            cur.select(QTextCursor.WordUnderCursor)
        cur.beginEditBlock()
        cur.setCharFormat(QTextCharFormat())
        bf = QTextBlockFormat()
        cur.setBlockFormat(bf)
        cur.endEditBlock()


    # ---- Absatz ---------------------------------------------------------------
