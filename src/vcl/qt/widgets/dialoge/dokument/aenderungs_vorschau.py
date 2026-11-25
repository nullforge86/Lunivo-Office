"""Änderungsvorschau: schreibgeschütztes Feld, das Stücke ``(art, text)`` zeigt — „entfernt“ durchgestrichen, „neu“ unterstrichen, „gleich“ normal.

Nur ``QTextDocument``/``QTextCursor``/``QTextCharFormat``. Farben kommen aus den Rollen ``Farbe.ENTFERNT``/``Farbe.NEU`` (vom Thema gesetzt), Maße aus ``mass.py``.
Die Höhe folgt dem Text bis ``CHAT_VORSCHAU_MAX``, darüber rollt das Feld; mit ``frei=True`` füllt das Feld den vom Layout gegebenen Platz (Vorher/Nachher-Fenster) und rollt nur in sich. Es ist eine Anzeige (Karten-Art ``karte``), kein Eingabefeld."""
from __future__ import annotations

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QBrush, QColor, QTextCharFormat, QTextCursor, QTextDocument, QTextDocumentFragment
from PySide6.QtWidgets import QSizePolicy, QTextEdit

from framework.schnittstellen.datentypen.farben import Farbe
from core.text import ki_markdown
from vcl.qt.widgets.bausteine.farben.karte import als_karte
from vcl.qt.widgets.bausteine.abstaende.mass import AENDERUNG_DECKKRAFT, CHAT_VORSCHAU_MAX


def _hinterlegt(farbe: str) -> QBrush:
    c = QColor(farbe); c.setAlpha(AENDERUNG_DECKKRAFT)
    return QBrush(c)


class AenderungsVorschau(QTextEdit):
    def __init__(self, stuecke: list | None = None, *, frei: bool = False):
        super().__init__()
        self._frei = frei
        self._stuecke: list = []
        self.setReadOnly(True)               # lesbar und per Tab erreichbar (Bildschirmleser, Scrollen mit der Tastatur)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding if frei else QSizePolicy.Fixed)
        als_karte(self, "karte")
        self.stuecke_setzen(stuecke or [])

    def stuecke_setzen(self, stuecke: list, markdown: bool = False) -> None:
        """``markdown``: „neu“-Stücke sind Markdown und erscheinen so, wie sie ins Dokument kommen (Überschriften, Listen, Tabellen, Hervorhebungen)."""
        self._markdown = markdown
        self._stuecke = list(stuecke)
        self._zeichnen()

    def _format(self, art: str) -> QTextCharFormat:
        f = QTextCharFormat()
        if art == "entfernt":
            f.setFontStrikeOut(True); f.setBackground(_hinterlegt(Farbe.ENTFERNT))
        elif art == "neu":
            f.setFontUnderline(True); f.setBackground(_hinterlegt(Farbe.NEU))
        return f

    @staticmethod
    def _markdown_dokument(text: str) -> QTextDocument:
        """Markdown für die Anzeige in diesem Vorschaufeld lesen (nur Darstellung; die Übernahme ins Dokument geht über die zentrale Bearbeitung)."""
        d = QTextDocument()
        d.setMarkdown(ki_markdown.normalisieren(text), QTextDocument.MarkdownDialectGitHub)
        return d

    def _zeichnen(self) -> None:
        doc = self.document(); doc.clear()
        c = QTextCursor(doc)
        for art, text in self._stuecke:
            if art == "neu" and getattr(self, "_markdown", False):
                von = c.position()
                c.insertFragment(QTextDocumentFragment(self._markdown_dokument(text)))
                m = QTextCursor(doc); m.setPosition(von); m.setPosition(c.position(), QTextCursor.KeepAnchor)
                m.mergeCharFormat(self._format(art))
                continue
            c.insertText(text, self._format(art))
        if self._frei:
            c.movePosition(QTextCursor.Start); self.setTextCursor(c)       # das Feld beginnt oben, nicht am Ende des Textes
        self._hoehe()

    def _hoehe(self) -> None:
        if self._frei:
            return
        doc = self.document()
        if self.viewport().width() > 0:
            doc.setTextWidth(self.viewport().width())
        self.setFixedHeight(min(CHAT_VORSCHAU_MAX, int(doc.size().height()) + 2 * self.frameWidth()))

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self._hoehe()

    def changeEvent(self, e) -> None:
        if e.type() in (QEvent.PaletteChange, QEvent.StyleChange) and hasattr(self, "_stuecke"):
            self._zeichnen()
        super().changeEvent(e)
