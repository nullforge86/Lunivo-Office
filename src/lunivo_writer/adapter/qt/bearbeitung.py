"""Bearbeiten: Brücke zwischen einem ``QTextDocument`` (der Ansicht der Oberfläche) und der Qt-freien Bearbeitungssitzung ``core.editing.Sitzung``.

``ModellSpiegel`` hält zu einem Textdokument das Modell und eine Sitzung bereit. Ändert die Oberfläche das Textdokument selbst (Tippen, Einfügen …), erkennt der Spiegel das an der
Änderungszahl des Dokuments und baut das Modell beim nächsten Zugriff neu auf; die Rückgängig-Liste des Textdokuments bleibt dann die der Oberfläche. Läuft eine Änderung über die
Sitzung (``einfuegen``, ``loeschen``, ``zeichenformat`` …), spielt der Spiegel dieselbe Änderung als einen Schritt auf dem Textdokument nach; Rückgängig und Wiederholen der
Sitzung gehen als ``undo``/``redo`` an das Textdokument. So bleiben Modell und Ansicht gleich, und der Weg ist Oberfläche → Adapter → Kern."""
from __future__ import annotations

from PySide6.QtCore import QUrl
from PySide6.QtGui import QImage, QTextBlockFormat, QTextCharFormat, QTextCursor, QTextDocument, QTextImageFormat, QTextListFormat, QTextTableCellFormat, QTextTableFormat

from lunivo_writer.adapter.qt.dokument import _Schreiben, _absatz_schreiben, _id, _setzen, document_from_qt, eigenschaften
from lunivo_writer.core.document.model import Paragraph, Table
from lunivo_writer.core.editing import Aenderung, Caret, Sitzung, absaetze
from lunivo_writer.core.editing.sitzung import behaelter, innerste_tabelle
from lunivo_writer.editor.objekte import bilddaten


GROSS = 6000                       # ab so vielen Absätzen baut ein Befehl das Modell nach einer Änderung der Oberfläche nicht neu auf (Neuaufbau: etwa 15 ms je 1000 Absätze, mit Formaten ein Mehrfaches): er arbeitet direkt am Textdokument


class ModellSpiegel:
    def __init__(self, qdoc: QTextDocument, seite=None):
        self.qdoc = qdoc
        self._seite = seite
        self._sitzung: Sitzung | None = None
        self._revision = -1
        self._pfade: list = []
        self._eigen = False

    # -- Modell und Sitzung --
    def seite_setzen(self, seite) -> None:
        self._seite = seite
        self._revision = -1

    def sitzung(self) -> Sitzung:
        """Die Sitzung zum jetzigen Stand des Textdokuments (neu aufgebaut, wenn die Oberfläche das Dokument seit dem letzten Zugriff selbst geändert hat)."""
        if self._sitzung is None or self.qdoc.revision() != self._revision:
            self._sitzung = Sitzung(document_from_qt(self.qdoc, self._seite))
            self._sitzung.beobachter.append(self._beobachten)
            self._pfade = [p for p, _a in absaetze(self._sitzung.dok)]
            self._revision = self.qdoc.revision()
        return self._sitzung

    def zu_gross(self) -> bool:
        """Soll der Befehl direkt am Textdokument arbeiten, weil das Modell neu aufgebaut werden müsste und das Dokument sehr groß ist (``GROSS``)?"""
        return self.veraltet() and self.qdoc.blockCount() > GROSS

    def veraltet(self) -> bool:
        """Hat die Oberfläche das Textdokument seit dem letzten Aufbau des Modells selbst geändert?"""
        return self._sitzung is None or self.qdoc.revision() != self._revision

    def modell(self):
        return self.sitzung().dok

    # -- Stellen zwischen Qt und Modell --
    def caret(self, position: int) -> Caret:
        self.sitzung()
        b = self.qdoc.findBlock(position)
        return Caret(self._pfade[b.blockNumber()], position - b.position())

    def position(self, caret: Caret) -> int:
        return self.qdoc.findBlockByNumber(self._pfade.index(caret.pfad)).position() + caret.versatz

    def cursor_uebernehmen(self, cursor: QTextCursor) -> None:
        """Schreibmarke und Auswahl des Textcursors in die Sitzung übernehmen (``Sitzung.cursor``/``anker``)."""
        s = self.sitzung()
        s.auswaehlen(self.caret(cursor.anchor()), self.caret(cursor.position()))

    def cursor_setzen(self, cursor: QTextCursor) -> None:
        """Schreibmarke und Auswahl der Sitzung auf den Textcursor legen (zum Beispiel nach ``Sitzung.bewegen``)."""
        s = self.sitzung()
        cursor.setPosition(self.position(s.anker if s.anker is not None else s.cursor))
        cursor.setPosition(self.position(s.cursor), QTextCursor.KeepAnchor)

    # -- Befehle der Oberfläche --
    def zeichenformat(self, cursor: QTextCursor, fmt: QTextCharFormat, entfernen: tuple = ()) -> bool:
        """Das Zeichenformat ``fmt`` auf die Auswahl des Cursors anwenden (über Modell und Sitzung). False, wenn nichts ausgewählt ist."""
        if not cursor.hasSelection() or (self.zu_gross()):
            return False
        s = self.sitzung()
        s.zeichenformat(eigenschaften(fmt), self.caret(cursor.selectionStart()), self.caret(cursor.selectionEnd()), entfernen)
        return True

    def absatzformat(self, cursor: QTextCursor, fmt: QTextBlockFormat, entfernen: tuple = ()) -> None:
        s = self.sitzung()
        a, b = self.caret(cursor.selectionStart()), self.caret(cursor.selectionEnd())
        s.absatzformat(eigenschaften(fmt), a, b, entfernen)

    def absatzformate(self, cursor: QTextCursor, fn) -> bool:
        """``fn(QTextBlockFormat)`` auf jeden Absatz der Auswahl anwenden (jeder Absatz mit seinen eigenen Werten), über Modell und Sitzung. False bei sehr großem Dokument."""
        if self.zu_gross():
            return False
        s = self.sitzung()
        von, bis = sorted((cursor.anchor(), cursor.position()))
        liste = []
        blk = self.qdoc.findBlock(von)
        while blk.isValid() and blk.position() <= bis:
            alt = blk.blockFormat()
            neu = QTextBlockFormat(alt)
            fn(neu)
            p_alt, p_neu = eigenschaften(alt), eigenschaften(neu)
            setzen = {k: v for k, v in p_neu.items() if p_alt.get(k) != v}
            entfernen = tuple(k for k in p_alt if k not in p_neu)
            if setzen or entfernen:
                liste.append((self._pfade[blk.blockNumber()], setzen, entfernen))
            blk = blk.next()
        s.absatzformate(liste)
        return True

    def einfuegen(self, cursor: QTextCursor, text: str, fmt: QTextCharFormat | None = None) -> None:
        """Text an die Stelle des Cursors setzen (eine Auswahl wird zuerst gelöscht); der Cursor steht danach hinter dem Text."""
        s = self.sitzung()
        if cursor.hasSelection():
            s.loeschen(self.caret(cursor.selectionStart()), self.caret(cursor.selectionEnd()))
            ziel = s.cursor
        else:
            ziel = self.caret(cursor.position())
        from lunivo_writer.core.document.model import CharacterFormat
        neu = s.einfuegen(text, ziel, CharacterFormat(eigenschaften(fmt)) if fmt is not None else None)
        cursor.setPosition(self.position(neu))

    def tippen(self, cursor: QTextCursor, text: str, fmt: QTextCharFormat) -> bool:
        """Getippten Text mit dem Schreibformat ``fmt`` an die Stelle des Cursors setzen (über Modell und Sitzung); mit Auswahl ersetzt er sie. False in sehr großen Dokumenten."""
        if self.zu_gross():
            return False
        if cursor.hasSelection():
            self.ersetzen(cursor, text, fmt)
            return True
        self._tippen = True
        try:
            self.einfuegen(cursor, text, fmt)
        finally:
            self._tippen = False
        return True

    def entfernen(self, cursor: QTextCursor, rueckwaerts: bool) -> bool:
        """Ein Zeichen vor (Rückschritt) oder hinter (Entf) dem Cursor löschen, solange es im selben Absatz liegt; mit Auswahl diese löschen (über Modell und Sitzung).
        False, wenn Qt es tun soll (Absatzgrenze, Dokumentanfang, sehr großes Dokument)."""
        if self.zu_gross():
            return False
        if cursor.hasSelection():
            self.loeschen(cursor)
            return True
        b = cursor.block()
        v = cursor.position() - b.position()
        s = self.sitzung()
        pfad = self._pfade[b.blockNumber()]
        if (rueckwaerts and v <= 0) or (not rueckwaerts and v >= b.length() - 1):
            # Absatzgrenze: nur zwischen Absätzen im selben Behälter (Abschnitt, Zelle, Rahmen) und ohne Liste/Tabelle dazwischen; sonst macht es Qt
            nachbar = b.previous() if rueckwaerts else b.next()
            if not nachbar.isValid() or nachbar.textList() is not None or b.textList() is not None:
                return False
            npfad = self._pfade[nachbar.blockNumber()]
            if npfad[:-1] != pfad[:-1] or abs(npfad[-1] - pfad[-1]) != 1:
                return False
            vorn, hinten = (npfad, pfad) if rueckwaerts else (pfad, npfad)
            von, bis = Caret(vorn, self._laenge(vorn)), Caret(hinten, 0)
        else:
            von, bis = (Caret(pfad, v - 1), Caret(pfad, v)) if rueckwaerts else (Caret(pfad, v), Caret(pfad, v + 1))
        self._tippen = True                                          # wie getippter Text: aufeinanderfolgendes Löschen ist für Qt ein Rückgängig-Schritt
        try:
            s.loeschen(von, bis)
        finally:
            self._tippen = False
        cursor.setPosition(self.position(von))
        return True

    def _laenge(self, pfad) -> int:
        from lunivo_writer.core.editing.sitzung import absatz_bei, laenge
        return laenge(absatz_bei(self._sitzung.dok, pfad))

    def ersetzen(self, cursor: QTextCursor, text: str, fmt: QTextCharFormat | None = None) -> None:
        """Die Auswahl durch ``text`` ersetzen (ohne Auswahl: einfügen); ein Schritt für Rückgängig. Der Cursor steht danach hinter dem Text."""
        s = self.sitzung()
        block = QTextCursor(self.qdoc)
        block.beginEditBlock()
        try:
            with s.gruppiert():
                self.einfuegen(cursor, text, fmt)
        finally:
            block.endEditBlock()
            self._revision = self.qdoc.revision()

    def loeschen(self, cursor: QTextCursor) -> None:
        if cursor.hasSelection():
            s = self.sitzung()
            s.loeschen(self.caret(cursor.selectionStart()), self.caret(cursor.selectionEnd()))
            cursor.setPosition(self.position(s.cursor))

    def rueckgaengig(self) -> bool:
        return self.sitzung().rueckgaengig()

    def wiederholen(self) -> bool:
        return self.sitzung().wiederholen()

    # -- Nachspielen auf dem Textdokument --
    def _beobachten(self, a: Aenderung, richtung: str) -> None:
        if self._eigen:
            return
        self._eigen = True
        try:
            if richtung == "zurueck":
                self.qdoc.undo()
            elif richtung == "wiederholen":
                self.qdoc.redo()
            else:
                c = QTextCursor(self.qdoc)
                if self.__dict__.get("_tippen"):                              # getippter Text: ohne Bearbeitungsblock, damit Qt aufeinanderfolgende Zeichen zu einem Rückgängig-Schritt zusammenfasst
                    self._nachspielen(a, c)
                else:
                    c.beginEditBlock()
                    try:
                        self._nachspielen(a, c)
                    finally:
                        c.endEditBlock()
            self._pfade_neu()
            self._revision = -1 if self.__dict__.pop("_revision_ungueltig", False) else self.qdoc.revision()
        finally:
            self._eigen = False

    def _pfade_neu(self) -> None:
        self._pfade = [p for p, _a in absaetze(self._sitzung.dok)]

    def _vor(self, caret: Caret) -> int:
        """Qt-Position der Stelle im Textdokument VOR der Änderung (die Absätze davor sind unverändert, ihr Index bleibt)."""
        return self.qdoc.findBlockByNumber(self._index(caret.pfad)).position() + caret.versatz

    def _index(self, pfad) -> int:
        """Die Blocknummer des Absatzes im Textdokument VOR der Änderung (``_pfade`` gilt bis nach dem Nachspielen für den Stand davor, auch für Absätze, die die Änderung verschmilzt)."""
        return self._pfade.index(pfad)

    def _nachspielen(self, a: Aenderung, c: QTextCursor) -> None:
        p = a.parameter
        if a.art == "text":
            pos = self._vor(p["caret"])
            c.setPosition(pos)
            cf = QTextCharFormat()                                         # immer das Format des Modells, damit Ansicht und Modell gleich bleiben
            _setzen(cf, p["format"])
            for k, stueck in enumerate(p["text"].split("\n")):
                if k:
                    c.insertBlock(c.blockFormat(), c.blockCharFormat())          # der neue Absatz erbt Absatz- und Zeichenformat des geteilten
                if stueck:
                    c.insertText(stueck, cf)
        elif a.art == "loeschen":
            von, bis = self._vor(p["von"]), self._vor(p["bis"])
            if self.__dict__.get("_tippen") and bis - von == 1:           # ein Zeichen wie beim Rückschritt: Qt fasst aufeinanderfolgendes Löschen zu einem Schritt zusammen
                c.setPosition(bis)
                c.deletePreviousChar()
            else:
                c.setPosition(von)
                c.setPosition(bis, QTextCursor.KeepAnchor)
                c.removeSelectedText()
        elif a.art == "bild":
            c.setPosition(self._vor(p["caret"]))
            bild = p["bild"]
            fmt = QTextImageFormat()
            _setzen(fmt, bild.format.properties)
            if bild.raster_png:
                img = QImage.fromData(bild.raster_png, "PNG")
                self.qdoc.addResource(QTextDocument.ImageResource, QUrl(fmt.name()), img)
                if bild.original:
                    bilddaten.merken(img, bild.original, bild.fallback_png, bild.raster_only)
            c.insertImage(fmt)
        elif a.art == "tabelle":
            c.setPosition(self._vor(p["caret"]))
            tf = QTextTableFormat()
            _setzen(tf, p["eigenschaften"])
            t = c.insertTable(p["zeilen"], p["spalten"], tf)
            self._tabelle_aus_qt(a, t)
        elif a.art == "liste_anlegen":
            lf = QTextListFormat()
            _setzen(lf, p["eigenschaften"])
            erster = self.qdoc.findBlockByNumber(self._index(p["absaetze"][0]))
            letzter = self.qdoc.findBlockByNumber(self._index(p["absaetze"][-1]))
            c.setPosition(erster.position())
            c.setPosition(letzter.position(), QTextCursor.KeepAnchor)
            c.createList(lf)
        elif a.art == "liste_entfernen":
            blk = self.qdoc.findBlockByNumber(self._index(p["absatz"]))
            lst = blk.textList()
            if lst is not None:
                lst.remove(blk)
            bc = QTextCursor(blk)
            bf = bc.blockFormat(); bf.setIndent(0); bf.setLeftMargin(0); bc.setBlockFormat(bf)
        elif a.art == "freies_objekt":
            from lunivo_writer.editor.objekte import freie_bilder as FB
            blk = self.qdoc.findBlockByNumber(self._index(p["absatz"]))
            if p["neuer_absatz"]:
                c.setPosition(blk.position() + blk.length() - 1)
                c.insertBlock(QTextBlockFormat())
                blk = c.block()
            bild = a.medien[p["name"]]
            img = QImage.fromData(bild.raster_png, "PNG")
            self.qdoc.addResource(QTextDocument.ImageResource, QUrl(p["name"]), img)
            if bild.original:
                bilddaten.merken(img, bild.original, bild.fallback_png, bild.raster_only)
            FB.an_absatz(QTextCursor(blk), dict(p["angabe"], n=p["name"]))
        elif a.art == "zellen_verbinden":
            t = QTextCursor(self.qdoc.findBlockByNumber(self._index(p["tabelle"] + (0, 0, 0)))).currentTable()
            t.mergeCells(*p["rechteck"])
            self._revision_ungueltig = True                              # Qt führt die Inhalte der Zellen zusammen: das Modell wird neu gelesen
        elif a.art == "tabellenformat":
            t = QTextCursor(self.qdoc.findBlockByNumber(self._index(p["tabelle"] + (0, 0, 0)))).currentTable()
            f = t.format()
            for name in p["entfernen"]:
                f.clearProperty(_id(name))
            _setzen(f, p["setzen"])
            t.setFormat(f)
        elif a.art == "zellformat":
            t = QTextCursor(self.qdoc.findBlockByNumber(self._index(p["tabelle"] + (0, 0, 0)))).currentTable()
            zelle = t.cellAt(*p["zelle"])
            f = zelle.format().toTableCellFormat()
            for name in p["entfernen"]:
                f.clearProperty(_id(name))
            _setzen(f, p["setzen"])
            zelle.setFormat(f)
        elif a.art == "zelle_teilen":
            from lunivo_writer.editor.tabelle.tabelleneigenschaften import zelle_teilen
            t = QTextCursor(self.qdoc.findBlockByNumber(self._index(p["tabelle"] + (0, 0, 0)))).currentTable()
            zelle = t.cellAt(*p["zelle"])
            zelle_teilen(t, zelle.firstCursorPosition(), *p["teilung"])
            self._revision_ungueltig = True                              # Qt vergibt die Formate der neuen Zellen: das Modell wird neu gelesen
        elif a.art == "tabellenstruktur":
            t = QTextCursor(self.qdoc.findBlockByNumber(self._index(p["tabelle"] + (0, 0, 0)))).currentTable()
            {"zeilen_einfuegen": t.insertRows, "zeilen_loeschen": t.removeRows, "spalten_einfuegen": t.insertColumns, "spalten_loeschen": t.removeColumns}[p["art"]](p["index"], p["anzahl"])
            self._revision_ungueltig = True                              # Qt vergibt die Zellformate: das Modell wird beim nächsten Zugriff aus dem Textdokument neu gelesen
        elif a.art == "absatzformate":
            for pfad, setzen, entfernen in p["liste"]:
                blk = self.qdoc.findBlockByNumber(self._index(pfad))
                bf = blk.blockFormat()
                for name in entfernen:
                    bf.clearProperty(_id(name))
                _setzen(bf, setzen)
                QTextCursor(blk).setBlockFormat(bf)
        elif a.art == "zeichenformat" and not p["entfernen"]:
            c.setPosition(self._vor(p["von"]))
            c.setPosition(self._vor(p["bis"]), QTextCursor.KeepAnchor)
            cf = QTextCharFormat()
            _setzen(cf, p["eigenschaften"])
            c.mergeCharFormat(cf)
        elif a.art == "absatzformat" and not p["entfernen"]:
            c.setPosition(self._vor(p["von"]))
            c.setPosition(self._vor(p["bis"]), QTextCursor.KeepAnchor)
            bf = QTextBlockFormat()
            _setzen(bf, p["eigenschaften"])
            c.mergeBlockFormat(bf)
        else:
            for er in a.ersetzungen:                                       # sonst: die betroffenen Absätze aus dem Modell neu schreiben
                self._absaetze_ersetzen(er, c)

    def _tabelle_aus_qt(self, a: Aenderung, t) -> None:
        """Die Formate, die Qt der neuen Tabelle gegeben hat (Zellformate, Tabellenformat), ins Modell übernehmen: die Tabelle im Modell, in der Änderung (für Wiederholen) und im Dokument."""
        zelle = eigenschaften(t.cellAt(0, 0).format())
        tab_props = eigenschaften(t.format())
        pfad = a.ersetzungen[0].behaelter
        start = a.ersetzungen[0].start
        for nach in (behaelter(self._sitzung.dok, pfad)[start + 2], a.ersetzungen[0].neu[2]):      # der Absatz nach der Tabelle trägt in Qt das Zellformat als Zeichenformat
            nach.format.char_format.properties = dict(zelle)
        for tab in (self._sitzung.dok_tabelle(pfad, a.ersetzungen[0].start + 1), a.ersetzungen[0].neu[1]):
            tab.properties = dict(tab_props)
            for zeile in tab.table_rows:
                for z in zeile.cells:
                    z.properties = dict(zelle)
                    for blk in z.content:
                        if isinstance(blk, Paragraph):
                            blk.format.char_format.properties = dict(zelle)

    def freies_bild_einfuegen(self, cursor: QTextCursor, img: QImage, angabe: dict, neuer_absatz: bool) -> tuple[int, int]:
        """Ein Bild frei am Absatz des Cursors verankern (über Modell und Sitzung). → (Blocknummer, Index der Angabe im Absatz)."""
        from lunivo_writer.adapter.qt.dokument import bild_aus_qimage
        from lunivo_writer.editor.objekte import freie_bilder as FB
        s = self.sitzung()
        name = FB.neuer_name(self.qdoc)
        pfad = self._pfade[cursor.block().blockNumber()]
        s.freies_bild_einfuegen(pfad, name, bild_aus_qimage(img), angabe, neuer_absatz)
        nr = cursor.block().blockNumber() + (1 if neuer_absatz else 0)
        return nr, len(FB.aus_absatz(self.qdoc.findBlockByNumber(nr).blockFormat())) - 1

    def zellen_verbinden(self, cursor: QTextCursor) -> bool:
        """Die markierten Tabellenzellen verbinden (über Modell und Sitzung)."""
        t = cursor.currentTable()
        if t is None or not cursor.hasSelection() or (self.zu_gross()):
            return False
        r, n, c, m = cursor.selectedTableCells()
        s = self.sitzung()
        tabelle = innerste_tabelle(s.dok, self._pfade[cursor.block().blockNumber()])
        if tabelle is None or n * m < 2:
            return False
        s.zellen_verbinden(tabelle, r, c, n, m)
        return True

    def liste_umschalten(self, cursor: QTextCursor, stil) -> bool:
        """Liste am Absatz des Cursors an- oder ausschalten (gleicher Stil schaltet aus); über Modell und Sitzung. False in sehr großen Dokumenten."""
        if self.zu_gross():
            return False
        s = self.sitzung()
        pfad = self._pfade[cursor.block().blockNumber()]
        lst = cursor.currentList()
        if lst is not None and lst.format().style() == stil:
            s.liste_entfernen(pfad)
            return True
        fmt = QTextListFormat()
        fmt.setStyle(stil)
        fmt.setIndent(1)
        von, bis = sorted((cursor.anchor(), cursor.position()))
        nr_von, nr_bis = self.qdoc.findBlock(von).blockNumber(), self.qdoc.findBlock(bis).blockNumber()
        s.liste_anlegen([self._pfade[n] for n in range(nr_von, nr_bis + 1)], eigenschaften(fmt))
        return True

    def tabellenformat(self, tabelle, fn) -> bool:
        """``fn(QTextTableFormat)`` auf das Format der Qt-Tabelle ``tabelle`` anwenden (über Modell und Sitzung). False in sehr großen Dokumenten."""
        if self.zu_gross():
            return False
        s = self.sitzung()
        alt = tabelle.format()
        neu = QTextTableFormat(alt)
        fn(neu)
        p_alt, p_neu = eigenschaften(alt), eigenschaften(neu)
        setzen = {k: v for k, v in p_neu.items() if p_alt.get(k) != v}
        entfernen = tuple(k for k in p_alt if k not in p_neu)
        if not setzen and not entfernen:
            return True
        pfad = innerste_tabelle(s.dok, self._pfade[tabelle.cellAt(0, 0).firstCursorPosition().block().blockNumber()])
        if pfad is None:
            return False
        s.tabellenformat(pfad, setzen, entfernen)
        return True

    def zellformat(self, zelle, fn) -> bool:
        """``fn(QTextTableCellFormat)`` auf das Format der Qt-Zelle ``zelle`` anwenden (über Modell und Sitzung). False in sehr großen Dokumenten."""
        if self.zu_gross():
            return False
        s = self.sitzung()
        alt = zelle.format().toTableCellFormat()
        neu = QTextTableCellFormat(alt)
        fn(neu)
        p_alt, p_neu = eigenschaften(alt), eigenschaften(neu)
        setzen = {k: v for k, v in p_neu.items() if p_alt.get(k) != v}
        entfernen = tuple(k for k in p_alt if k not in p_neu)
        if not setzen and not entfernen:
            return True
        tabelle = innerste_tabelle(s.dok, self._pfade[zelle.firstCursorPosition().block().blockNumber()])
        if tabelle is None:
            return False
        s.zellformat(tabelle, (zelle.row(), zelle.column()), setzen, entfernen)
        return True

    def zelle_teilen(self, cursor: QTextCursor, spalten: int, zeilen: int) -> bool:
        """Die Zelle am Cursor teilen (über Modell und Sitzung). False bei verbundener Zelle oder sehr großem Dokument (dann teilt die Oberfläche wie bisher)."""
        t = cursor.currentTable()
        if t is None or (self.zu_gross()):
            return False
        s = self.sitzung()
        tabelle = innerste_tabelle(s.dok, self._pfade[cursor.block().blockNumber()])
        z = t.cellAt(cursor)
        return tabelle is not None and s.zelle_teilen(tabelle, z.row(), z.column(), spalten, zeilen)

    def tabelle_aendern(self, cursor: QTextCursor, art: str, anzahl: int = 1) -> bool:
        """Zeilen oder Spalten der Tabelle am Cursor einfügen oder löschen: ``art`` ``zeile_oben`` | ``zeile_unten`` | ``spalte_links`` | ``spalte_rechts`` | ``zeile_loeschen`` | ``spalte_loeschen``.
        False, wenn der Cursor in keiner Tabelle steht oder das Dokument sehr groß ist."""
        t = cursor.currentTable()
        if t is None or (self.zu_gross()):
            return False
        z = t.cellAt(cursor)
        s = self.sitzung()
        pfad = self._pfade[cursor.block().blockNumber()]
        tabelle = innerste_tabelle(s.dok, pfad)
        if tabelle is None:
            return False
        art_n, index = {"zeile_oben": ("zeilen_einfuegen", z.row()), "zeile_unten": ("zeilen_einfuegen", z.row() + z.rowSpan()),
                        "spalte_links": ("spalten_einfuegen", z.column()), "spalte_rechts": ("spalten_einfuegen", z.column() + z.columnSpan()),
                        "zeile_loeschen": ("zeilen_loeschen", z.row()), "spalte_loeschen": ("spalten_loeschen", z.column())}[art]
        s.tabelle_aendern(tabelle, art_n, index, anzahl)
        return True

    def tabelle_einfuegen(self, cursor: QTextCursor, zeilen: int, spalten: int, fmt: QTextTableFormat):
        """Eine Tabelle an der Stelle des Cursors einfügen (über Modell und Sitzung). → Cursor in der ersten Zelle."""
        s = self.sitzung()
        neu = s.tabelle_einfuegen(zeilen, spalten, eigenschaften(fmt), self.caret(cursor.position()))
        cursor.setPosition(self.position(neu))
        return cursor

    def _absaetze_ersetzen(self, er, c: QTextCursor) -> None:
        n = self._index(er.behaelter + (er.start,))
        erster = self.qdoc.findBlockByNumber(n)
        letzter = self.qdoc.findBlockByNumber(n + len(er.alt) - 1)
        c.setPosition(erster.position())
        c.setPosition(letzter.position() + letzter.length() - 1, QTextCursor.KeepAnchor)
        c.removeSelectedText()
        ctx = _Schreiben(self.qdoc, self._sitzung.dok)
        for i, neu in enumerate(er.neu):
            if isinstance(neu, Paragraph):
                _absatz_schreiben(c, neu, ctx, i == 0, None)
