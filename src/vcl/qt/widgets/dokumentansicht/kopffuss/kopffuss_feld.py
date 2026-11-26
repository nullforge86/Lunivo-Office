"""Das Textfeld über dem Kopf- bzw. Fußbereich des Blattes: randlos, gestrichelter Rahmen, Papierfarben unabhängig vom Thema.

Das Feld ist ein Eingabefeld: sein Text geht über die Seiteneinrichtung an das Dokument (``KopfFussBearbeiter.speichern``). Die Felder für
Seitennummer und Seitenanzahl stehen im Feld als Zahl mit grauem Grund und werden beim Lesen wieder zu ihrer Schreibweise im Text."""
from __future__ import annotations

import re

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QTextCharFormat, QTextCursor, QTextFormat
from PySide6.QtWidgets import QPlainTextEdit, QWidget

from writer.funktionen.kopffuss import blatttexte as T
from vcl.qt.widgets.bausteine.farben import KOPFFUSS_FELDGRUND, papierfeld
from vcl.qt.widgets.dokumentansicht.kopffuss.strich import strichstift

FELD_EIGENSCHAFT = int(QTextFormat.UserProperty) + 1          # im Zeichenformat: welches Feld die Zahl zeigt
_FELDER = re.compile(r"\{(" + T.FELD_SEITEN + "|" + T.FELD_SEITE + r")\}")


class KopfFussFeld(QPlainTextEdit):
    """``schliessen``: Esc gedrückt; ``fokus``: die Schreibmarke kam in dieses Feld (Zone)."""
    schliessen = Signal()
    fokus = Signal(str)

    def __init__(self, eltern: QWidget, zone: str):
        super().__init__(eltern)
        self.zone = zone
        self.setFrameShape(QPlainTextEdit.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAccessibleName(T.ZONENNAMEN[zone])
        papierfeld(self)                                          # das Feld steht auf dem weißen Papier
        self.setCursorWidth(1)
        self.basis = QTextCharFormat()                            # das Zeichenformat der ganzen Zeile (Schrift, Größe, F/K/U, Farbe)

    # ---- Felder für Seitennummer und Seitenanzahl ----------------------------------------------------------------------------------------
    @staticmethod
    def _feld_format(art: str) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setProperty(FELD_EIGENSCHAFT, art)
        f.setBackground(QColor(KOPFFUSS_FELDGRUND))
        return f

    def felder_setzen(self, text: str, zahlen: dict) -> None:
        """Den Text ins Feld schreiben; jedes Feld erscheint als die Zahl aus ``zahlen`` (Schlüssel: Name des Feldes)."""
        self.clear()
        c = QTextCursor(self.document())
        for i, zeile in enumerate(text.split("\n")):
            if i:
                c.insertBlock()
            rest = 0
            for m in _FELDER.finditer(zeile):
                c.insertText(zeile[rest:m.start()], QTextCharFormat())
                c.insertText(zahlen.get(m.group(1), m.group(1)), self._feld_format(m.group(1)))
                rest = m.end()
            c.insertText(zeile[rest:], QTextCharFormat())

    def text_lesen(self) -> str:
        """Der Text, in dem jedes Feld wieder in seiner Schreibweise steht."""
        zeilen = []
        block = self.document().begin()
        while block.isValid():
            teile = []
            it = block.begin()
            while not it.atEnd():
                stueck = it.fragment()
                art = stueck.charFormat().property(FELD_EIGENSCHAFT)
                teile.append("{" + art + "}" if art else stueck.text())
                it += 1
            zeilen.append("".join(teile))
            block = block.next()
        return "\n".join(zeilen)

    def basis_setzen(self, basis: QTextCharFormat) -> None:
        """Das Zeichenformat der ganzen Zeile setzen: jedes Textstück bekommt genau ``basis`` (auch weggenommene Eigenschaften wirken),
        die Felder für Seitennummer und Seitenanzahl behalten dazu ihren grauen Grund."""
        self.basis = basis
        stuecke = []
        block = self.document().begin()
        while block.isValid():
            it = block.begin()
            while not it.atEnd():
                stueck = it.fragment()
                stuecke.append((stueck.position(), stueck.length(), stueck.charFormat().property(FELD_EIGENSCHAFT)))
                it += 1
            block = block.next()
        c = QTextCursor(self.document())
        c.joinPreviousEditBlock()                                 # gehört zum vorigen Schritt: kein eigener Rückgängig-Schritt für die Zeilenschrift
        for anfang, laenge, art in stuecke:
            format_ = QTextCharFormat(basis)
            if art:
                format_.merge(self._feld_format(art))
            c.setPosition(anfang)
            c.setPosition(anfang + laenge, QTextCursor.KeepAnchor)
            c.setCharFormat(format_)
        c.endEditBlock()
        self.setCurrentCharFormat(basis)

    def _feld_bei(self, pos: int) -> dict:
        """(Anfang, Ende) des Feldes, das die Zeichen vor/hinter ``pos`` berührt – getrennt nach ``davor`` und ``dahinter``."""
        c = QTextCursor(self.document())
        gefunden = {}
        for seite, p in (("davor", pos - 1), ("dahinter", pos)):
            if p < 0 or p >= self.document().characterCount() - 1:
                continue
            c.setPosition(p)
            c.setPosition(p + 1, QTextCursor.KeepAnchor)
            if c.charFormat().property(FELD_EIGENSCHAFT):
                it = self.document().findBlock(p).begin()
                while not it.atEnd():
                    stueck = it.fragment()
                    if stueck.position() <= p < stueck.position() + stueck.length():
                        gefunden[seite] = (stueck.position(), stueck.position() + stueck.length())
                        break
                    it += 1
        return gefunden

    def focusInEvent(self, ev) -> None:
        super().focusInEvent(ev)
        self.fokus.emit(self.zone)

    def keyPressEvent(self, ev) -> None:
        if ev.key() == Qt.Key_Escape:
            self.schliessen.emit()
            return
        c = self.textCursor()
        if ev.key() in (Qt.Key_Backspace, Qt.Key_Delete) and not c.hasSelection():
            feld = self._feld_bei(c.position()).get("davor" if ev.key() == Qt.Key_Backspace else "dahinter")
            if feld:                                              # das Feld ganz löschen
                c.setPosition(feld[0])
                c.setPosition(feld[1], QTextCursor.KeepAnchor)
                c.removeSelectedText()
                self.setCurrentCharFormat(self.basis)
                return
        elif ev.text() and ev.text().isprintable() and not (ev.modifiers() & (Qt.ControlModifier | Qt.AltModifier)) and not c.hasSelection():
            nah = self._feld_bei(c.position())
            if "davor" in nah and nah.get("davor") == nah.get("dahinter"):     # mitten im Feld: dahinter schreiben
                c.setPosition(nah["davor"][1])
                self.setTextCursor(c)
            self.setCurrentCharFormat(self.basis)                 # Tippen neben dem Feld erbt dessen Hintergrund nicht
        super().keyPressEvent(ev)

    def paintEvent(self, ev) -> None:
        super().paintEvent(ev)
        p = QPainter(self.viewport())
        p.setPen(strichstift())
        p.drawRect(self.viewport().rect().adjusted(0, 0, -1, -1))
