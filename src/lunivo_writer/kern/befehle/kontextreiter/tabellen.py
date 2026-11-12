"""Befehle: Kontext-Reiter „Tabellentools“, Aufbau: Zeilen/Spalten einfügen und löschen, Zellen verbinden/teilen, Tabelle teilen, Eigenschaften.

Ein Baustein von ``KontextBefehle`` (``kern/befehle/kontextreiter/kontext.py``) und damit von ``Befehle`` (siehe ``kern/befehlsliste.py``)."""
from __future__ import annotations

from PySide6.QtGui import QTextCursor
from lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster import EingabeFenster


class TabellenBefehle:
    # ==== Tabellentools (Kontext) ===================================================================================================
    def _tab(self):
        e = self.ed
        if not e:
            return None, None, None
        c = e.textCursor()
        t = None if e.isReadOnly() else c.currentTable()               # im Nur-Lesen-Modus gibt es keine Tabelle zum Ändern
        return (e, c, t) if t else (e, c, None)

    def tabelleZeileOben(self, k=None):
        e, c, t = self._tab()
        if t and not e.modell_spiegel().tabelle_aendern(c, "zeile_oben"): t.insertRows(t.cellAt(c).row(), 1)

    def tabelleZeileUnten(self, k=None):
        e, c, t = self._tab()
        if t and not e.modell_spiegel().tabelle_aendern(c, "zeile_unten"): t.insertRows(t.cellAt(c).row() + 1, 1)

    def tabelleSpalteLinks(self, k=None):
        e, c, t = self._tab()
        if t and not e.modell_spiegel().tabelle_aendern(c, "spalte_links"): t.insertColumns(t.cellAt(c).column(), 1)

    def tabelleSpalteRechts(self, k=None):
        e, c, t = self._tab()
        if t and not e.modell_spiegel().tabelle_aendern(c, "spalte_rechts"): t.insertColumns(t.cellAt(c).column() + 1, 1)

    def tabelleZeileLoeschen(self, k=None):
        e, c, t = self._tab()
        if t and t.rows() > 1:
            if not e.modell_spiegel().tabelle_aendern(c, "zeile_loeschen"): t.removeRows(t.cellAt(c).row(), 1)
        elif t: self.tabelleLoeschen()

    def tabelleSpalteLoeschen(self, k=None):
        e, c, t = self._tab()
        if t and t.columns() > 1:
            if not e.modell_spiegel().tabelle_aendern(c, "spalte_loeschen"): t.removeColumns(t.cellAt(c).column(), 1)
        elif t: self.tabelleLoeschen()

    def tabelleLoeschen(self, k=None):
        e, c, t = self._tab()
        if t:
            first = t.firstCursorPosition().position() - 1
            last = t.lastCursorPosition().position() + 1
            cc = QTextCursor(e.document())
            cc.setPosition(max(0, first)); cc.setPosition(min(last, e.document().characterCount() - 1), QTextCursor.KeepAnchor)
            cc.removeSelectedText()

    _ZELLEN_LOESCHEN = {"Zellen nach links verschieben": "links", "Zellen nach oben verschieben": "oben",
                        "Ganze Zeile löschen": "zeile", "Ganze Spalte löschen": "spalte"}

    def tabelleZellenLoeschen(self, k=None):
        """Löschen ▸ Zellen löschen …: Auswahl, wie die Lücke geschlossen wird (Logik: ``editor/tabelle/tabelleneigenschaften.zellen_loeschen``)."""
        e, c, t = self._tab()
        if not t:
            return
        n, ok = EingabeFenster.getItem(self.w, "Zellen löschen", "Löschen:", list(self._ZELLEN_LOESCHEN), 0, False)
        if not ok:
            return
        art = self._ZELLEN_LOESCHEN[n]
        if art == "zeile":
            return self.tabelleZeileLoeschen()
        if art == "spalte":
            return self.tabelleSpalteLoeschen()
        from lunivo_writer.editor.tabelle.tabelleneigenschaften import zellen_loeschen
        meldung = zellen_loeschen(t, e.textCursor(), art)
        if meldung:
            self.w.lbl_msg.setText(meldung)
        else:
            e.document().setModified(True)

    def tabelleVerbinden(self, k=None):
        e, c, t = self._tab()
        if t and c.hasSelection() and not e.modell_spiegel().zellen_verbinden(c): t.mergeCells(c)

    def tabelleTeilen(self, k=None):
        e, c, t = self._tab()
        if not t: return
        from lunivo_writer.editor.tabelle.tabelleneigenschaften import zelle_teilen
        text, ok = EingabeFenster.getText(self.w, "Zellen teilen", "Spalten,Zeilen:", text="2,1")
        if not ok: return
        try:
            sp, ze = (int(x) for x in text.replace(";", ",").split(","))
            if not (1 <= sp <= 20 and 1 <= ze <= 20): raise ValueError
        except ValueError:
            self.w.lbl_msg.setText("Ungültige Eingabe: bitte „Spalten,Zeilen“ angeben, zum Beispiel 2,1.")
            return
        if e.modell_spiegel().zelle_teilen(e.textCursor(), sp, ze) or zelle_teilen(t, e.textCursor(), sp, ze): e.document().setModified(True)

    def tabelleTabelleTeilen(self, k=None):
        """Tabelle oberhalb der Zeile der Schreibmarke teilen: die Zeilen ab hier kommen in eine neue Tabelle darunter."""
        e, c, t = self._tab()
        if not t:
            return
        r = t.cellAt(c).row()
        if r < 1:
            self.w.lbl_msg.setText("Die Schreibmarke muss unterhalb der ersten Zeile stehen, damit die Tabelle geteilt werden kann.")
            return
        zeilen = []
        for zr in range(r, t.rows()):
            zeilen.append([QTextCursor(t.cellAt(zr, sp).firstCursorPosition()) for sp in range(t.columns())])
        frag = []
        for zeile in zeilen:
            reihe = []
            for z in zeile:
                z.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                reihe.append(z.selection())
            frag.append(reihe)
        fmt = t.format()
        c.beginEditBlock()
        t.removeRows(r, t.rows() - r)
        ende = QTextCursor(t.lastCursorPosition())
        ende.movePosition(QTextCursor.NextBlock)
        ende.insertBlock()
        neu = ende.insertTable(len(frag), len(frag[0]), fmt)
        for zr, reihe in enumerate(frag):
            for sp, f in enumerate(reihe):
                neu.cellAt(zr, sp).firstCursorPosition().insertFragment(f)
        c.endEditBlock()
        e.document().setModified(True)

    def tabelleEigenschaften(self, k=None):
        e, c, t = self._tab()
        if not t:
            return
        from lunivo_writer.editor.tabelle import tabelleneigenschaften as TE
        from lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel import ausfuehren
        from lunivo_writer.oberflaeche.dialoge.dokument_dialoge import TabellenEigenschaftenDialog
        d = TabellenEigenschaftenDialog(self.w, werte=TE.lesen(t, c))
        if ausfuehren(d):
            TE.anwenden(t, c, d.werte())
            fm = t.format()
            fm.setHeaderRowCount(1 if d.kopf.isChecked() else 0)
            t.setFormat(fm)
            e.document().setModified(True)

    def _tabellen_aktionsmenue(self, name: str):
        """Menü „Einfügen“ bzw. „Löschen“ aus der gemeinsamen Definition (``kern/tabellenaktionen.py``): Band, Mini-Leiste und Kontextmenü."""
        from lunivo_writer.kern.tabellenaktionen import GRUPPEN
        from lunivo_writer.oberflaeche.bauteile import symbole
        from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for a in GRUPPEN[name]:
            m.eintrag(a.name, lambda bf=a.befehl: self.tun(bf), symbol=symbole.icon(a.symbol, 16) if symbole.hat(a.symbol) else None)
        return m

    def menue_tabelleEinfuegenAktionen(self):
        return self._tabellen_aktionsmenue("Einfügen")

    def menue_tabelleLoeschenAktionen(self):
        return self._tabellen_aktionsmenue("Löschen")
