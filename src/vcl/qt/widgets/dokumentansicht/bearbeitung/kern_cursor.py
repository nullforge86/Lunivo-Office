"""Kern cursor: aus ``vcl.qt.widgets.dokumentansicht.bearbeitung.kern_editor`` herausgelöst."""
from __future__ import annotations
from writer.funktionen import bearbeiten as _bearbeiten


class KernCursor:
    """Ein Textzeiger mit den gebräuchlichen Aufrufen eines Qt-Textcursors, aber auf dem Dokumentmodell: Stellen sind Zeichenstellen im Rohtext
    (Absätze durch ein Zeichen getrennt). Er startet an der Auswahl des Editors; ``KernEditor.setTextCursor`` übernimmt seine Stellen.
    Schreibende Aufrufe (``insertText``, ``removeSelectedText``) wirken über die Bearbeitungssitzung an der Auswahl des Editors."""

    class MoveMode:
        MoveAnchor, KeepAnchor = 0, 1

    class MoveOperation:
        NoMove, Start, StartOfLine, StartOfBlock, StartOfWord, PreviousBlock, PreviousCharacter, PreviousWord = 0, 1, 2, 3, 4, 5, 6, 7
        EndOfLine, EndOfWord, EndOfBlock, NextBlock, NextCharacter, NextWord, End = 8, 9, 10, 11, 12, 13, 14

    class SelectionType:
        WordUnderCursor, LineUnderCursor, BlockUnderCursor, Document = 0, 1, 2, 3

    MoveAnchor, KeepAnchor = 0, 1
    NoMove, Start, StartOfLine, StartOfBlock, StartOfWord, PreviousBlock, PreviousCharacter, PreviousWord = 0, 1, 2, 3, 4, 5, 6, 7
    EndOfLine, EndOfWord, EndOfBlock, NextBlock, NextCharacter, NextWord, End = 8, 9, 10, 11, 12, 13, 14
    WordUnderCursor, LineUnderCursor, BlockUnderCursor, Document = 0, 1, 2, 3

    def __init__(self, editor: "KernEditor"):
        self._e = editor
        a = _bearbeiten.auswahl(editor.kennung)
        self._anker, self._kopf = editor.position_im_text(a.anker), editor.position_im_text(a.kopf)

    # ---- Stellen ---------------------------------------------------------------------------------------------------------------------
    def _text(self) -> str:
        return self._e.rohtext()

    def _ende(self) -> int:
        return len(self._text())

    def position(self) -> int:
        return self._kopf

    def anchor(self) -> int:
        return self._anker

    def hasSelection(self) -> bool:
        return self._anker != self._kopf

    def selectionStart(self) -> int:
        return min(self._anker, self._kopf)

    def selectionEnd(self) -> int:
        return max(self._anker, self._kopf)

    def selectedText(self) -> str:
        return self._text()[self.selectionStart():self.selectionEnd()]

    def setPosition(self, pos: int, mode: int = 0) -> None:
        pos = max(0, min(int(pos), self._ende()))
        self._kopf = pos
        if not mode:
            self._anker = pos

    def clearSelection(self) -> None:
        self._anker = self._kopf

    def atBlockEnd(self) -> bool:
        return self._kopf >= self._absatz_grenzen(self._kopf)[1]

    def atBlockStart(self) -> bool:
        return self._kopf <= self._absatz_grenzen(self._kopf)[0]

    def atStart(self) -> bool:
        return self._kopf == 0

    def atEnd(self) -> bool:
        return self._kopf >= self._ende()

    def _absatz_grenzen(self, pos: int) -> tuple:
        """(Anfang, Ende) des Absatzes, in dem die Stelle liegt (Stellen im Rohtext)."""
        n = 0
        for _aid, laenge in _bearbeiten.dok_absatzlaengen(self._e.kennung):
            if pos <= n + laenge:
                return n, n + laenge
            n += laenge + 1
        return n, n

    def movePosition(self, op: int, mode: int = 0, n: int = 1) -> bool:
        t, k = self._text(), self._kopf
        for _ in range(max(1, n)):
            if op == self.Start:
                k = 0
            elif op == self.End:
                k = len(t)
            elif op in (self.StartOfBlock, self.StartOfLine):
                k = self._absatz_grenzen(k)[0]
            elif op in (self.EndOfBlock, self.EndOfLine):
                k = self._absatz_grenzen(k)[1]
            elif op == self.NextCharacter:
                k = min(len(t), k + 1)
            elif op == self.PreviousCharacter:
                k = max(0, k - 1)
            elif op == self.NextBlock:
                k = min(len(t), self._absatz_grenzen(k)[1] + 1)
            elif op == self.PreviousBlock:
                von = self._absatz_grenzen(k)[0]
                k = self._absatz_grenzen(max(0, von - 1))[0] if von > 0 else 0
            elif op in (self.StartOfWord, self.PreviousWord):
                while k > 0 and not t[k - 1].isalnum():
                    k -= 1
                while k > 0 and t[k - 1].isalnum():
                    k -= 1
            elif op in (self.EndOfWord, self.NextWord):
                while k < len(t) and not t[k].isalnum():
                    k += 1
                while k < len(t) and t[k].isalnum():
                    k += 1
        self._kopf = k
        if not mode:
            self._anker = k
        return True

    def select(self, art: int) -> None:
        t, k = self._text(), self._kopf
        if art == self.Document:
            self._anker, self._kopf = 0, len(t)
        elif art in (self.BlockUnderCursor, self.LineUnderCursor):
            self._anker, self._kopf = self._absatz_grenzen(k)
        else:
            von = bis = k
            while von > 0 and t[von - 1].isalnum():
                von -= 1
            while bis < len(t) and t[bis].isalnum():
                bis += 1
            self._anker, self._kopf = von, bis

    # ---- Schreiben (über die Sitzung des Editors) ----------------------------------------------------------------------------------
    def _uebernehmen(self) -> None:
        self._e.setTextCursor(self)

    def insertText(self, text: str, _format=None) -> None:
        """Fügt Text an dieser Stelle ein (eine Auswahl wird ersetzt); ein übergebenes Qt-Format bedeutet: ohne Zeichenformat des Umfelds."""
        self._uebernehmen()
        self._e.ansicht._befehl(lambda: _bearbeiten.aenderung_text_einfuegen(self._e.kennung, text, format={} if _format is not None else None))
        self._anker = self._kopf = self._e.position_im_text(_bearbeiten.auswahl(self._e.kennung).kopf)

    def removeSelectedText(self) -> None:
        self._uebernehmen()
        self._e.ansicht._befehl(lambda: _bearbeiten.aenderung_loeschen(self._e.kennung))
        self._anker = self._kopf = self._e.position_im_text(_bearbeiten.auswahl(self._e.kennung).kopf)

    def beginEditBlock(self) -> None:
        pass

    def endEditBlock(self) -> None:
        pass

    # ---- Umfeld ----------------------------------------------------------------------------------------------------------------------
    def currentTable(self):
        """Die Tabelle, in der die Schreibmarke steht (sonst ``None``)."""
        return self._e.tabelle_an_marke()

    def currentList(self):
        """Die Liste des Absatzes an der Schreibmarke (sonst ``None``)."""
        return self._e.liste_an_marke()
