"""PDF- und Bildexport für das Hauptfenster."""
from __future__ import annotations

import os
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox, QWidget
from writer.anbindung import dateizugriff as _dateizugriff
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
        ordner = os.path.dirname(t.path) if t.path else (self.settings.get("pdf/ordner", "") or self.settings.get("speichern/ordner", "")
                                                          or self.settings.get("last_dir", os.path.expanduser("~")))
        return _dateizugriff.pdf_wahl(pfad=os.path.join(ordner, (os.path.splitext(t.title)[0] or "Unbenannt") + ".pdf"),
                                      druck=self.settings.get("pdf/recht_druck", "frei") or "frei",
                                      **{feld: self.settings.get_bool(schl, vorgabe) for feld, (schl, vorgabe) in self.PDF_SCHLUESSEL.items()})

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
        from vcl.qt.drucken.bild_export import bilder_schreiben
        from vcl.qt.widgets.bausteine.symbole.medien.bild_export import BildExportAnsicht
        t = self.current_tab()
        if not t:
            return QWidget()

        def exportieren(wahl):
            bilder = bilder_schreiben(t.editor.kennung, t.title, wahl)
            self.settings.set("export/bild_ordner", wahl.ordner)
            if bilder:
                self.statusBar().showMessage(f"{len(bilder)} Bild{'er' if len(bilder) != 1 else ''} exportiert.", 5000)
            return bilder

        return BildExportAnsicht(self.backstage, self.settings.get("export/bild_ordner", "") or "",
                                 self.ausgabe_ppi(), exportieren, self.backstage_schliessen)

    def _pdf_schreiben(self, t: DocumentTab, path: str, wahl=None) -> bool:
        """Schreibt die PDF. Ohne ``wahl`` (Weg über „Speichern unter“) gelten die gemerkten Exportoptionen, ganzes Dokument, ohne Kennwort."""
        if wahl is None:
            wahl = _dateizugriff.pdf_wahl_mit(self.pdf_wahl_start(t), pfad=path)
        try:
            autor = self.dokumente.meta_fuer_speichern(t.meta).get("author", "") if wahl.eigenschaften else ""
            titel = os.path.splitext(t.title)[0] if wahl.eigenschaften else ""
            n = _dateizugriff.pdf_schreiben(t.editor.kennung, path, wahl, titel, autor, t.editor.current_page())
        except Exception as e:  # PDF-Ausgabe darf das Programm nicht beenden
            QMessageBox.critical(self, "PDF-Export fehlgeschlagen", f"Die PDF-Datei wurde nicht erstellt.\n\nGrund: {e}\n\nWählen Sie einen anderen Ordner oder Dateinamen.")
            return False
        self.statusBar().showMessage(f"PDF gespeichert ({n} Seiten): {path}", 5000)
        if self.settings.get_bool("pdf/oeffnen", False):
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        return True
