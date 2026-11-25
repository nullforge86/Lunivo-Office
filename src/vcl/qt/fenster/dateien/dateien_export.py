"""PDF- und Bildexport für das Hauptfenster."""
from __future__ import annotations

import os
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox, QWidget
from framework.dokumentverwaltung.dateizugriff import sicher_schreiben
from vcl.qt.widgets.dokumentansicht.dokumentfenster.dokument_bereich import DocumentTab


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
        from filter.pdf.pdf_export import PdfWahl
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
        from vcl.qt.widgets.dialoge.dokument.pdf_export import PdfExportAnsicht
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
        from framework.dokumentverwaltung.ausgabe.bild_export import bilder_schreiben
        from vcl.qt.widgets.bausteine.symbole.medien.bild_export import BildExportAnsicht
        t = self.current_tab()
        if not t:
            return QWidget()

        def exportieren(wahl):
            bilder = bilder_schreiben(t.modell_fuer_speichern(), t.title, wahl)
            self.settings.set("export/bild_ordner", wahl.ordner)
            if bilder:
                self.statusBar().showMessage(f"{len(bilder)} Bild{'er' if len(bilder) != 1 else ''} exportiert.", 5000)
            return bilder

        return BildExportAnsicht(self.backstage, self.settings.get("export/bild_ordner", "") or "",
                                 self.ausgabe_ppi(), exportieren, self.backstage_schliessen)

    def _pdf_schreiben(self, t: DocumentTab, path: str, wahl=None) -> bool:
        """Schreibt die PDF. Ohne ``wahl`` (Weg über „Speichern unter“) gelten die gemerkten Exportoptionen, ganzes Dokument, ohne Kennwort."""
        from filter.pdf import pdf_export as PE
        if wahl is None:
            wahl = self.pdf_wahl_start(t)
            wahl.pfad = path
        try:
            autor = self.dokumente.meta_fuer_speichern(t.meta).get("author", "") if wahl.eigenschaften else ""
            titel = os.path.splitext(t.title)[0] if wahl.eigenschaften else ""
            erste, letzte = PE.seiten(wahl, t.editor.current_page())
            dokument = t.modell_fuer_speichern()
            if wahl.bereich == "markierung":
                dokument = PE.nur_markierung(dokument, t.editor.sitzung.auswahl)

            def erzeugen(tmp):
                from filter.pdf.pdf_ausgabe import dokument_als_pdf
                struktur = {"lesezeichen": PE.lesezeichen(wahl), "kommentare": wahl.kommentare, "hyperlinks": wahl.hyperlinks, "notenlinks": wahl.notenlinks}
                n = dokument_als_pdf(dokument, tmp, titel, autor=autor, erste=erste, letzte=letzte, struktur=struktur)
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
