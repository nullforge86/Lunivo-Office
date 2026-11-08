"""Einfügen aus Zwischenablage und nachträgliche Einfügeoptionen."""
from __future__ import annotations

from PySide6.QtCore import QMimeData, Qt, QUrl
from PySide6.QtGui import QFont, QImage, QTextCharFormat, QTextCursor, QTextDocument, QTextDocumentFragment, QTextFormat, QTextImageFormat

from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf
from lunivo_writer.ui.baukasten.basis.mass import ICON_KLEIN, PADDING_EDITOR_KNOPF, RADIUS_KLEIN, SCHRIFT_KLEIN

EINFUEGE_MODI = ["Quellformatierung beibehalten", "Zielformatierung verwenden", "Nur Text"]


def _ziel_fragment(html: str, standard: QFont):
    """HTML einfügen, aber Schriftart, -größe, Farben und Hintergründe des Ziels behalten (Fett, Kursiv, Verweise bleiben)."""
    from PySide6.QtGui import QBrush
    d = QTextDocument()
    d.setHtml(html)
    c = QTextCursor(d)
    c.select(QTextCursor.Document)
    b = d.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            fr = it.fragment()
            if fr.isValid() and not fr.charFormat().isImageFormat():
                f = QTextCharFormat(fr.charFormat())
                f.clearProperty(QTextFormat.FontFamilies); f.clearProperty(QTextFormat.FontFamily)
                f.clearProperty(QTextFormat.FontPointSize); f.clearProperty(QTextFormat.FontPixelSize)
                f.clearForeground(); f.clearBackground()
                k = QTextCursor(d); k.setPosition(fr.position()); k.setPosition(fr.position() + fr.length(), QTextCursor.KeepAnchor)
                k.setCharFormat(f)
            it += 1
        b = b.next()
    return QTextDocumentFragment(d)


class EinfuegenMixin:
    """Kapselt Einfügen, Formatvarianten und die kleine Einfüge-Schaltfläche."""

    def insertFromMimeData(self, source) -> None:
        if source.hasImage() and not source.hasHtml():
            img = QImage(source.imageData())
            if not img.isNull():
                name = f"einfuegen-{self.document().revision()}"
                self.document().addResource(QTextDocument.ImageResource, QUrl(name), img)
                f = QTextImageFormat(); f.setName(name)
                f.setWidth(min(img.width(), self.page.content_width_px)); f.setHeight(
                    img.height() * min(1.0, self.page.content_width_px / max(1, img.width())))
                self.textCursor().insertImage(f)
                return
        modus = self.opt_text("bearbeiten/einfuegen_standard", EINFUEGE_MODI[0])
        if not isinstance(modus, str) or modus not in EINFUEGE_MODI:
            modus = EINFUEGE_MODI[0]
        self._einfuegen_mit(source, modus, neu=True)

    def _einfuegen_mit(self, source, modus: str, neu: bool) -> None:
        """Einfügen als EIN Rückgängig-Schritt; danach bietet die kleine Schaltfläche die anderen Formen an (Optionen ▸ Bearbeiten)."""
        c = self.textCursor()
        c.beginEditBlock()
        start = c.selectionStart()
        c.removeSelectedText()
        if modus == "Nur Text" or not source.hasHtml():
            c.insertText(source.text() if source.hasText() else "")
        elif modus == "Zielformatierung verwenden":
            c.insertFragment(_ziel_fragment(source.html(), self.document().defaultFont()))
        else:
            c.insertFragment(QTextDocumentFragment.fromHtml(source.html()))
        ende = c.position()
        c.endEditBlock()
        self.setTextCursor(c)
        if neu and self.opt("bearbeiten/einfuegen_schaltflaeche", True) and ende > start and not self.isReadOnly():
            kopie = QMimeData()
            for f in source.formats():
                kopie.setData(f, source.data(f))
            self._einfuegen_schaltflaeche(kopie, start, ende, modus)

    def _einfuegen_schaltflaeche(self, quelle, start: int, ende: int, modus: str) -> None:
        from PySide6.QtWidgets import QMenu, QToolButton
        b = getattr(self, "_paste_btn", None)
        if b is None:
            b = self._paste_btn = DropdownKnopf(self.viewport())
            from lunivo_writer.ui.widgets import icons
            b.setText("Einfügen"); b.setIcon(icons.icon("clipboard-paste", ICON_KLEIN))
            b.setCursor(Qt.ArrowCursor)
            b.setStyleSheet("QToolButton { border: 1px solid palette(mid); border-radius: " f"{RADIUS_KLEIN}" "px; padding: " f"{PADDING_EDITOR_KNOPF}" "; "
                            "background: palette(window); font-size: " f"{SCHRIFT_KLEIN}" "pt; }")
            self.cursorPositionChanged.connect(self._paste_btn_pruefen)
        self._paste_ende = ende
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe(b)
        for name in EINFUEGE_MODI:
            m.eintrag(name, lambda name=name: self._einfuegen_neu(quelle, start, name), haken=(name == modus))
        b.menue_setzen(m, geteilt=False)
        c = QTextCursor(self.document()); c.setPosition(ende)
        r = self.cursorRect(c)
        b.move(max(0, r.left()), r.bottom() + 2)
        b.adjustSize()
        b.show()

    def _einfuegen_neu(self, quelle, start: int, modus: str) -> None:
        c = QTextCursor(self.document())
        c.setPosition(start)
        c.setPosition(self._paste_ende, QTextCursor.KeepAnchor)
        self.setTextCursor(c)
        self._paste_btn.hide()
        self._einfuegen_mit(quelle, modus, neu=False)
        self._einfuegen_schaltflaeche(quelle, start, self.textCursor().position(), modus)

    def _paste_btn_pruefen(self) -> None:
        b = getattr(self, "_paste_btn", None)
        if b is not None and b.isVisible() and self.textCursor().position() != getattr(self, "_paste_ende", -1):
            b.hide()
