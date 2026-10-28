"""Befehle: Verweise."""
from __future__ import annotations

from PySide6.QtWidgets import QInputDialog, QMessageBox


class VerweiseBefehle:
    """Befehle des Bandes: Verweise. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""


    # ---- Verweise: Beschriftungen, Textmarken, Querverweise, Index, Zitate -------------------------------------
    def beschriftung(self, k=None):
        """Fenster „Beschriftung“: die Nummer steht schon im Feld („Tabelle 1“), dahinter schreibt man weiter. Eigene Bezeichnungen
        merkt sich Lunivo in den Einstellungen."""
        e = self.ed
        if not e:
            return
        import json
        from lunivo_writer.editor import verweise
        from lunivo_writer.ui.dialogs.verweise_fenster import BeschriftungDialog
        try:
            eigene = [str(x) for x in json.loads(self.w.settings.get("verweise/beschriftungen", "[]") or "[]")]
        except (ValueError, TypeError):
            eigene = []
        c = e.textCursor()
        objekt = c.currentTable() is not None or (c.hasSelection() and "\ufffc" in c.selectedText())
        d = BeschriftungDialog(self.w, eigene, lambda label, zahl: verweise.naechste_nummer(e, label, zahl), objekt=objekt,
                               label="Tabelle" if c.currentTable() is not None else "Abbildung")
        ok = d.exec()
        if d.eigene != eigene:
            self.w.settings.set("verweise/beschriftungen", json.dumps(d.eigene, ensure_ascii=False))
        if ok:
            r = d.ergebnis()
            verweise.beschriftung_einfuegen(e, r["label"], "", r["oben"], nach=r["nach"], ohne_bezeichnung=r["ohne"], zahl=r["zahl"])


    def _verzeichnis(self, art, titel, leer):
        if not self.ed:
            return
        from lunivo_writer.editor.verzeichnis import verzeichnis_einfuegen
        if verzeichnis_einfuegen(self.ed, art) == 0:
            QMessageBox.information(self.w, titel, leer)


    def abbildungsverzeichnis(self, k=None):
        self._verzeichnis("abb", "Abbildungsverzeichnis", "Es gibt keine Beschriftungen „Abbildung“. Fügen Sie sie über Verweise ▸ Beschriftung ein.")


    def stichwortverzeichnis(self, k=None):
        self._verzeichnis("index", "Stichwortverzeichnis", "Es sind keine Stichwörter markiert. Verwenden Sie Verweise ▸ Indexeintrag.")


    def literaturverzeichnis(self, k=None):
        self._verzeichnis("lit", "Literaturverzeichnis", "Es sind keine Quellen angelegt (Verweise ▸ Neue Quelle).")


    def textmarke(self, k=None):
        if self.ed:
            from lunivo_writer.ui.dialogs.verweise_dialoge import TextmarkeDialog
            TextmarkeDialog(self.w, self.ed).exec()


    def querverweis(self, k=None):
        """Fenster „Querverweis“: „Einfügen“ setzt den Verweis an die Schreibmarke, das Fenster bleibt offen."""
        e = self.ed
        if not e:
            return
        from lunivo_writer.editor import verweise
        from lunivo_writer.ui.dialogs.verweise_fenster import QuerverweisDialog
        d = QuerverweisDialog(self.w, verweise.querverweis_ziele(e))
        d.einfuegen.connect(lambda ziel, wie, link, oben_unten: verweise.querverweis_einfuegen(e, ziel, wie, link=link,
                                                                                               oben_unten=oben_unten))
        d.exec()


    def indexEintrag(self, k=None):
        """Fenster „Indexeintrag festlegen“: „Markieren“ setzt den Eintrag an die Markierung, „Alles markieren“ an jede Stelle
        mit demselben Text; das Fenster bleibt offen, bis „Schließen“."""
        if not self.ed:
            return
        from lunivo_writer.editor import verweise
        from lunivo_writer.ui.dialogs.verweise_fenster import IndexeintragDialog
        c = self.ed.textCursor()
        d = IndexeintragDialog(self.w, c.selectedText().strip() if c.hasSelection() else "",
                               [m["name"] for m in verweise.lesezeichen_liste(self.ed, versteckte=False)], c.hasSelection())

        def markieren(eintrag, alle):
            n = verweise.index_eintragen(self.ed, eintrag, alle)
            self.w.statusBar().showMessage(f"{n} Indexeintrag markiert." if n == 1 else f"{n} Indexeinträge markiert."
                                           if n else "Bitte Text markieren oder in ein Wort klicken.", 4000)
        d.markieren.connect(markieren)
        d.exec()


    def indexAktualisieren(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import verzeichnis as V
        if not V.vorhanden(self.ed.document(), "index"):
            self.w.statusBar().showMessage("Im Dokument gibt es noch keinen Index (Verweise ▸ Index einfügen).", 4000)
            return
        V.verzeichnis_aktualisieren(self.ed, "index")


    def inhaltsverzeichnisAktualisieren(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import verzeichnis as V
        if not V.vorhanden(self.ed.document(), "toc"):
            self.w.statusBar().showMessage("Im Dokument gibt es noch kein Inhaltsverzeichnis (Verweise ▸ TOC einfügen).", 4000)
            return
        V.verzeichnis_aktualisieren(self.ed, "toc")


    # ---- Klappe „Inhaltsverzeichnis“: Gliederungsebene des Absatzes ------------------------------------------------------
    def menue_inhaltsverzeichnisKlappe(self):
        """Ebene 1–9 und Textkörper wie in der Vorlage. In Lunivo trägt die Ebene die Formatvorlage „Überschrift N“
        (Textkörper: „Standard“); das Inhaltsverzeichnis nimmt diese Absätze auf. Der Haken zeigt die Ebene am Zeiger."""
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        eintraege = [m.eintrag(f"Ebene &{n}", lambda n=n: self.inhaltsEbene(None, n), haken=False) for n in range(1, 10)]
        eintraege.append(m.eintrag("Textkörper(&B)", lambda: self.inhaltsEbene(None, 0), haken=False))

        def auffrischen():
            jetzt = self.ed.textCursor().blockFormat().headingLevel() if self.ed else -1
            for i, a in enumerate(eintraege):
                a.setEnabled(self.ed is not None)
                a.setChecked((i + 1 if i < 9 else 0) == jetzt)
        m.aboutToShow.connect(auffrischen)
        return m


    def inhaltsEbene(self, k=None, ebene: int = 0):
        if self.ed:
            self.ed.apply_style(f"Überschrift {ebene}" if ebene else "Standard")


    # ---- Fuß- und Endnoten einzeln durchgehen ---------------------------------------------------------------------------
    def _note_gehe(self, delta, art, titel):
        if self.ed and self.ed.note_springen(delta, art) is None:
            self.w.statusBar().showMessage(f"Im Dokument gibt es keine {titel}.", 3000)

    def fussnoteZurueck(self, k=None): self._note_gehe(-1, "f", "Fußnoten")

    def fussnoteWeiter(self, k=None): self._note_gehe(1, "f", "Fußnoten")

    def endnoteZurueck(self, k=None): self._note_gehe(-1, "e", "Endnoten")

    def endnoteWeiter(self, k=None): self._note_gehe(1, "e", "Endnoten")


    def quelleNeu(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import verweise
        from lunivo_writer.ui.dialogs.verweise_dialoge import QuelleDialog
        d = QuelleDialog(self.w)
        if d.exec():
            q = d.ergebnis(); q["tag"] = verweise.quelle_tag(self.ed.quellen, q)
            self.ed.quellen.append(q); self.ed.document().setModified(True)


    def quellenVerwalten(self, k=None):
        if self.ed:
            from lunivo_writer.ui.dialogs.verweise_dialoge import QuellenDialog
            QuellenDialog(self.w, self.ed).exec()


    def zitat(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import verweise
        from lunivo_writer.editor.literatur import eintrag
        if not self.ed.quellen:
            QMessageBox.information(self.w, "Zitat", "Es sind noch keine Quellen angelegt. Verwenden Sie „Neue Quelle“.")
            return
        namen = [eintrag(q, self.ed.zitierweise) for q in self.ed.quellen]
        n, ok = QInputDialog.getItem(self.w, "Zitat einfügen", "Quelle:", namen, 0, False)
        if ok:
            verweise.zitat_einfuegen(self.ed, self.ed.quellen[namen.index(n)])


    def zitierweise(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor.literatur import ZITIERWEISEN
        n, ok = QInputDialog.getItem(self.w, "Zitierweise", "Zitierweise:", ZITIERWEISEN, ZITIERWEISEN.index(self.ed.zitierweise) if self.ed.zitierweise in ZITIERWEISEN else 0, False)
        if ok:
            self.ed.zitierweise = n
            self.ed._meta["zitierweise"] = n
            self.ed.document().setModified(True)
