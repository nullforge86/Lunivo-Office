"""Aktionen der Knöpfe im Reiter „Verweise“: öffnet die Dialoge und ruft die Befehle des Farmworks auf (Beschriftung, Verzeichnisse, Textmarke, Querverweis,
Index, Noten, Quellen, Zitat)."""
from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from framework.befehle.verweise.konstanten import ZITIERWEISEN_NAMEN
from vcl.qt.widgets.dialoge.dokument.eingabe_fenster import EingabeFenster
from vcl.qt.widgets.dialoge.verweise.beschriftung_dialog import BeschriftungDialog
from vcl.qt.widgets.dialoge.verweise.indexeintrag_dialog import IndexeintragDialog
from vcl.qt.widgets.dialoge.verweise.querverweis_dialog import QuerverweisDialog
from vcl.qt.widgets.dialoge.verweise.quelle_dialog import QuelleDialog
from vcl.qt.widgets.dialoge.verweise.quellen_dialog import QuellenDialog
from vcl.qt.widgets.dialoge.verweise.textmarke_dialog import TextmarkeDialog


class VerweiseAktionen:
    # ---- Beschriftungen, Textmarken, Querverweise, Index, Zitate -------------------------------------------------------
    def beschriftung(self, k=None):
        """Fenster „Beschriftung“: die Nummer steht schon im Feld („Tabelle 1“), dahinter schreibt man weiter. Eigene Bezeichnungen
        merkt sich Lunivo in den Einstellungen."""
        fw = self._vw()
        if fw is None:
            return
        start = fw.beschriftung_vorbereiten()
        d = BeschriftungDialog(self.w, list(start.eigene), fw.naechste_nummer, objekt=start.objekt, label=start.label)
        ok = d.exec()
        if tuple(d.eigene) != start.eigene:
            fw.eigene_beschriftungen_speichern(d.eigene)
        if ok:
            r = d.ergebnis()
            fw.beschriftung_einfuegen(r["label"], r["oben"], r["nach"], r["ohne"], r["zahl"])

    def _verzeichnis(self, art, titel, leer):
        fw = self._vw()
        if fw is not None and fw.verzeichnis_einfuegen(art) == 0:
            QMessageBox.information(self.w, titel, leer)

    def abbildungsverzeichnis(self, k=None):
        self._verzeichnis("abb", "Abbildungsverzeichnis", "Es gibt keine Beschriftungen „Abbildung“. Fügen Sie sie über Verweise ▸ Beschriftung ein.")

    def stichwortverzeichnis(self, k=None):
        self._verzeichnis("index", "Stichwortverzeichnis", "Es sind keine Stichwörter markiert. Verwenden Sie Verweise ▸ Indexeintrag.")

    def literaturverzeichnis(self, k=None):
        self._verzeichnis("lit", "Literaturverzeichnis", "Es sind keine Quellen angelegt (Verweise ▸ Neue Quelle).")

    def textmarke(self, k=None):
        fw = self._vw()
        if fw is not None:
            TextmarkeDialog(self.w, fw).exec()

    def querverweis(self, k=None):
        """Fenster „Querverweis“: „Einfügen“ setzt den Verweis an die Schreibmarke, das Fenster bleibt offen."""
        fw = self._vw()
        if fw is None:
            return
        d = QuerverweisDialog(self.w, fw.querverweis_ziele())
        d.einfuegen.connect(lambda ziel, wie, link, oben_unten: fw.querverweis_einfuegen(ziel, wie, link, oben_unten))
        d.exec()

    def indexEintrag(self, k=None):
        """Fenster „Indexeintrag festlegen“: „Markieren“ setzt den Eintrag an die Markierung, „Alles markieren“ an jede Stelle
        mit demselben Text; das Fenster bleibt offen, bis „Schließen“."""
        fw = self._vw()
        if fw is None:
            return
        start = fw.index_vorbereiten()
        d = IndexeintragDialog(self.w, start.vorschlag, list(start.marken), start.auswahl)
        d.markieren.connect(lambda eintrag, alle: fw.index_markieren(eintrag, alle))
        d.exec()

    def indexAktualisieren(self, k=None):
        fw = self._vw()
        if fw is not None:
            fw.verzeichnis_aktualisieren("index", "Im Dokument gibt es noch keinen Index (Verweise ▸ Index einfügen).")

    def inhaltsverzeichnisAktualisieren(self, k=None):
        fw = self._vw()
        if fw is not None:
            fw.verzeichnis_aktualisieren("toc", "Im Dokument gibt es noch kein Inhaltsverzeichnis (Verweise ▸ TOC einfügen).")

    def inhaltsEbene(self, k=None, ebene: int = 0):
        fw = self._vw()
        if fw is not None:
            fw.ebene_setzen(ebene)

    # ---- Fuß- und Endnoten einzeln durchgehen -----------------------------------------------------------------------------
    def _note_gehe(self, delta, art, titel):
        fw = self._vw()
        if fw is not None:
            fw.note_springen(delta, art, titel)

    def fussnoteZurueck(self, k=None): self._note_gehe(-1, "f", "Fußnoten")

    def fussnoteWeiter(self, k=None): self._note_gehe(1, "f", "Fußnoten")

    def endnoteZurueck(self, k=None): self._note_gehe(-1, "e", "Endnoten")

    def endnoteWeiter(self, k=None): self._note_gehe(1, "e", "Endnoten")

    # ---- Quellen und Zitate -----------------------------------------------------------------------------------------------
    def quelleNeu(self, k=None):
        fw = self._vw()
        if fw is None:
            return
        d = QuelleDialog(self.w)
        if d.exec():
            fw.quelle_neu(d.ergebnis())

    def quellenVerwalten(self, k=None):
        fw = self._vw()
        if fw is not None:
            QuellenDialog(self.w, fw).exec()

    def zitat(self, k=None):
        fw = self._vw()
        if fw is None:
            return
        quellen = fw.quellen()
        if not quellen:
            QMessageBox.information(self.w, "Zitat", "Es sind noch keine Quellen angelegt. Verwenden Sie „Neue Quelle“.")
            return
        namen = [fw.quelle_beschreibung(q) for q in quellen]
        n, ok = EingabeFenster.getItem(self.w, "Zitat einfügen", "Quelle:", namen, 0, False)
        if ok:
            fw.zitat_einfuegen(quellen[namen.index(n)]["tag"])

    def zitierweise(self, k=None):
        fw = self._vw()
        if fw is None:
            return
        weisen = list(ZITIERWEISEN_NAMEN)
        n, ok = EingabeFenster.getItem(self.w, "Zitierweise", "Zitierweise:", weisen, weisen.index(fw.zitierweise()) if fw.zitierweise() in weisen else 0, False)
        if ok:
            fw.zitierweise_setzen(n)
