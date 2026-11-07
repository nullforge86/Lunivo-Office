"""PDF- und Bildexport für das Hauptfenster."""
from __future__ import annotations

import os
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox, QWidget
from lunivo_writer.editor.pagination import export_pdf
from lunivo_writer.services import sicher_schreiben
from lunivo_writer.ui.document.document_area import DocumentTab


class DateienExportBaustein:
    """PDF- und Bildexportfunktionen des Hauptfensters."""

    # PDF-Exportoptionen ↔ gemerkte Einstellungen (dieselben Schlüssel wie unter Optionen ▸ Drucken)
    PDF_SCHLUESSEL = {"eigenschaften": ("pdf/eigenschaften", True), "kommentare": ("pdf/kommentare", False),
                      "hyperlinks": ("pdf/hyperlinks", True), "notenlinks": ("pdf/notenlinks", True),
                      "textmarken": ("pdf/lz_textmarken", False), "ueberschriften": ("pdf/lz_ueberschriften", False),
                      "andere": ("pdf/lz_andere", False), "eigene": ("pdf/lz_eigene", False),
                      "aendern": ("pdf/recht_aendern", True), "kopieren": ("pdf/recht_kopieren", True),
                      "kommentieren": ("pdf/recht_kommentieren", True), "schliessen": ("pdf/dlg_schliessen", True)}

    def pdf_wahl_start(self, t: DocumentTab):
        """Die Vorgaben für das PDF-Fenster und den PDF-Weg über „Speichern unter“ (Kennwörter werden nie gemerkt)."""
        from lunivo_writer.services.pdf_export import PdfWahl
        ordner = os.path.dirname(t.path) if t.path else (self.settings.get("pdf/ordner", "") or self.settings.get("speichern/ordner", "")
                                                          or self.settings.get("last_dir", os.path.expanduser("~")))
        w = PdfWahl(pfad=os.path.join(ordner, (os.path.splitext(t.title)[0] or "Unbenannt") + ".pdf"),
                    druck=self.settings.get("pdf/recht_druck", "frei") or "frei")
        for feld, (schl, vorgabe) in self.PDF_SCHLUESSEL.items():
            setattr(w, feld, self.settings.get_bool(schl, vorgabe))
        return w

    def export_pdf_dialog(self):
        """Öffnet den PDF-Export als Seite in der zweiten Spalte des Datei-Menüs."""
        t = self.current_tab()
        if not t:
            return
        self.backstage_oeffnen("pdf")

    def pdf_export_widget(self):
        """Baut die PDF-Exportseite des Datei-Menüs; alle Exportwahloptionen bleiben erhalten."""
        from lunivo_writer.ui.baukasten.pdf_export import PdfExportAnsicht
        t = self.current_tab()
        if not t:
            return QWidget()

        def exportieren(wahl) -> bool:
            if not self._darf_ueberschreiben(t, wahl.pfad) or not self._pdf_schreiben(t, wahl.pfad, wahl):
                return False
            for feld, (schl, _v) in self.PDF_SCHLUESSEL.items():
                self.settings.set(schl, getattr(wahl, feld))
            self.settings.set("pdf/recht_druck", wahl.druck)
            self.settings.set("pdf/ordner", os.path.dirname(wahl.pfad))
            return True

        e = t.editor
        return PdfExportAnsicht(self.backstage, self.pdf_wahl_start(t), max(1, e.page_count), e.current_page(),
                                e.textCursor().hasSelection(), exportieren, self.backstage_schliessen)

    def bild_export_widget(self):
        """Baut die Bildexportseite des Datei-Menüs; schreibt Bilder ohne ein separates Exportfenster."""
        from lunivo_writer.services.bild_export import bilder_schreiben
        from lunivo_writer.ui.baukasten.bild_export import BildExportAnsicht
        t = self.current_tab()
        if not t:
            return QWidget()

        def exportieren(wahl):
            bilder = bilder_schreiben(t.editor.document(), t.page, t.editor.noten, t.title, wahl)
            self.settings.set("export/bild_ordner", wahl.ordner)
            if bilder:
                self.statusBar().showMessage(f"{len(bilder)} Bild{'er' if len(bilder) != 1 else ''} exportiert.", 5000)
            return bilder

        return BildExportAnsicht(self.backstage, self.settings.get("export/bild_ordner", "") or "",
                                 self.ausgabe_ppi(), exportieren, self.backstage_schliessen)

    def _pdf_schreiben(self, t: DocumentTab, path: str, wahl=None) -> bool:
        """Schreibt die PDF. Ohne ``wahl`` (Weg über „Speichern unter“) gelten die gemerkten Exportoptionen, ganzes Dokument, ohne Kennwort."""
        from lunivo_writer.services import pdf_export as PE
        if wahl is None:
            wahl = self.pdf_wahl_start(t)
            wahl.pfad = path
        try:
            autor = self.dokumente.meta_fuer_speichern(t.meta).get("author", "") if wahl.eigenschaften else ""
            titel = os.path.splitext(t.title)[0] if wahl.eigenschaften else ""
            komm = None
            if wahl.kommentare:
                komm = {kid: f'{k.get("autor", "")}: {k.get("text", "")}'.strip(": ") for kid, k in t.editor.kommentare.items()}
            extra = {k: v for k, v in self.druckoptionen().items()
                     if k in ("versteckt", "felder_code", "zeichnungen", "balken", "hervorhebungen", "textmarken", "textgrenzen", "zuschnitt",
                              "blasen", "nur_formular")}
            extra.update(notenlinks=wahl.notenlinks, hyperlinks=wahl.hyperlinks)
            doc = t.editor.document()
            erste, letzte = PE.seiten(wahl, t.editor.current_page())
            if wahl.bereich == "markierung" and t.editor.textCursor().hasSelection():
                c = t.editor.textCursor()
                doc = PE.nur_markierung(doc, c.selectionStart(), c.selectionEnd())

            def erzeugen(tmp):
                n = export_pdf(tmp, doc, t.page, titel, autor, t.editor.noten, PE.lesezeichen(wahl),
                               self._silben_fuer_druck(), komm, extra, erste, letzte)
                PE.verschluesseln(tmp, wahl)
                return n
            n = sicher_schreiben.schreiben(path, erzeugen, endung=".pdf")
        except Exception as e:  # PDF-Ausgabe darf das Programm nicht beenden
            QMessageBox.critical(self, "PDF-Export fehlgeschlagen", f"Die PDF-Datei wurde nicht erstellt.\n\nGrund: {e}\n\nWählen Sie einen anderen Ordner oder Dateinamen.")
            return False
        self.statusBar().showMessage(f"PDF gespeichert ({n} Seiten): {path}", 5000)
        if self.settings.get_bool("pdf/oeffnen", False):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        return True
