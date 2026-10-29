"""Befehle: Datei, Vorlagen, Schutz."""
from __future__ import annotations

import os
from lunivo_writer.ui.baukasten.eingabe_fenster import EingabeFenster
from PySide6.QtWidgets import QLineEdit, QMenu, QMessageBox


class DateiBefehle:
    """Befehle des Bandes: Datei, Vorlagen, Schutz. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""


    # ---- Datei (☰-Menü und Schnellzugriff) ----------------------------------------------------------------
    def neu(self, k=None): self.w.new_document()

    def oeffnen(self, k=None): self.w.open_dialog()

    def speichern(self, k=None): self.w.save()

    def speichernUnter(self, k=None): self.w.save_as()

    def w_speichernAls(self, k=None, ext=".docx"): self.w.save_as_format(ext)

    def speichernPdf(self, k=None): self.w.export_pdf_dialog()

    def drucken(self, k=None): self.w.print_dialog()

    def vorschau(self, k=None): self.w.print_preview()

    def eigenschaften(self, k=None): self.w.show_info()

    def umbenennen(self, k=None): self.w.rename_document()

    def schliessen(self, k=None): self.w.close_tab(self.w.docs.currentIndex())

    def beenden(self, k=None): self.w.close()

    def ueber(self, k=None): self.w.about()

    def rueckgaengig(self, k=None):
        if self.ed: self.ed.undo()

    def wiederholen(self, k=None):
        if self.ed: self.ed.redo()


    # ---- Datei: Vorlagen, Schutz, Bildexport ---------------------------------------------------------------------
    def neuAusVorlage(self, k=None): self.w.neu_aus_vorlage()

    def vorlagenDurchsuchen(self, k=None): self.w.neu_aus_vorlage()


    def dokumentSchuetzen(self, k=None):
        t = self.w.current_tab()
        if not t:
            return
        wahl = ["Kennwort zum Öffnen setzen / ändern …", "Kennwort entfernen", "Bearbeitung sperren / freigeben"]
        n, ok = EingabeFenster.getItem(self.w, "Dokument schützen", "Was soll geschehen?", wahl, 0, False)
        if not ok:
            return
        if n == wahl[2]:
            self.w.toggle_sperre()
        elif n == wahl[1]:
            t.meta.pop("kennwort", None); t.editor.document().setModified(True)
            self.w.statusBar().showMessage("Kennwort entfernt — gilt ab dem nächsten Speichern.", 5000)
        else:
            a, ok = EingabeFenster.getText(self.w, "Kennwort", "Neues Kennwort:", kennwort=True)
            if ok and a:
                b, ok = EingabeFenster.getText(self.w, "Kennwort", "Zur Bestätigung noch einmal:", kennwort=True)
                if ok and a == b:
                    t.meta["kennwort"] = a; t.editor.document().setModified(True)
                    self.w.statusBar().showMessage("Das Dokument wird beim Speichern verschlüsselt (DOCX).", 5000)
                elif ok:
                    QMessageBox.information(self.w, "Kennwort", "Die Eingaben stimmen nicht überein.")


    def exportierenPng(self, k=None):
        """Öffnet den Bildexport in der rechten Spalte des Datei-Menüs."""
        if self.w.current_tab():
            self.w.backstage_oeffnen("bild")


    # ==== Datei (Reiter) =======================================================================================================
    def kopieSpeichern(self, k=None): self.w.save_copy()

    def exportierenDocx(self, k=None): self.w.export_as(".docx")

    def exportierenOdt(self, k=None): self.w.export_as(".odt")

    def exportierenTxt(self, k=None): self.w.export_as(".txt")

    def druckerWaehlen(self, k=None): self.w.print_dialog()


    def menue_zuletzt(self):
        m = QMenu()
        items = self.w.settings.recent()
        if not items:
            m.addAction("(keine)").setEnabled(False)
        for pfad in items:
            m.addAction(os.path.basename(pfad), lambda _=False, p=pfad: self.w.open_path(p)).setToolTip(pfad)
        return m
