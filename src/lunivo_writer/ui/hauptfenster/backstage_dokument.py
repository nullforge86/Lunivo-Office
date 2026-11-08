"""Dokumentaktionen aus der Backstage-Ansicht."""
from __future__ import annotations

import os
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox

from lunivo_writer.ui.baukasten.dokument.eingabe_fenster import EingabeFenster
from lunivo_writer.ui.baukasten.dokument.speichern_fenster import Dateifenster
from lunivo_writer.models.page import HeaderFooter
from lunivo_writer.ui.dialogs.dokument_dialoge import HeaderFooterDialog, TableDialog


class BackstageDokumentBaustein:
    """Umbenennen, Einfügen, Sperren und Kopf-/Fußzeilen eines Dokuments."""

    def rename_document(self):
        t = self.current_tab()
        if not t or not t.path:
            QMessageBox.information(self, "Umbenennen", "Das Dokument ist noch nicht gespeichert.")
            return
        neu, ok = EingabeFenster.getText(self, "Umbenennen", "Neuer Dateiname:", text=os.path.basename(t.path))
        if not ok or not neu.strip() or neu == os.path.basename(t.path):
            return
        ziel = os.path.join(os.path.dirname(t.path), neu.strip())
        if os.path.exists(ziel):
            QMessageBox.warning(self, "Umbenennen", "Eine Datei mit diesem Namen gibt es schon.")
            return
        try:
            os.rename(t.path, ziel)
        except OSError as e:
            QMessageBox.warning(self, "Umbenennen", f"Nicht möglich: {e.strerror or e}")
            return
        self.settings.remove_recent(t.path)
        t.set_path(ziel)
        self.settings.add_recent(ziel)
        self._update_tab_titles()


    def toggle_sperre(self):
        """Überprüfen ▸ Bearbeitung einschränken: Dokument schreibgeschützt (nur in dieser Sitzung)."""
        t = self.current_tab() if hasattr(self, "current_tab") else None
        if not t:
            return
        t.gesperrt = not getattr(t, "gesperrt", False)
        t.editor.setReadOnly(t.gesperrt or self.lesemodus)
        self.statusBar().showMessage("Bearbeitung gesperrt." if t.gesperrt else "Bearbeitung freigegeben.", 4000)


    def toggle_marks(self, on: bool):
        self.marken_setzen(on, on)


    def insert_table(self):
        if not self.current_editor():
            return
        d = TableDialog(self, (self.settings.get_int("tabelle/spalten", 5), self.settings.get_int("tabelle/zeilen", 2)))
        if d.exec():
            if d.speichern.isChecked():
                self.settings.set("tabelle/spalten", d.cols.value()); self.settings.set("tabelle/zeilen", d.rows.value())
            self._ed(lambda e: e.insert_table(d.rows.value(), d.cols.value(), spaltenbreite=d.spaltenbreite_px()))


    def insert_image(self):
        e = self.current_editor()
        if not e:
            return
        path, _ = Dateifenster.getOpenFileName(self, "Bild einfügen", self.settings.get("last_dir", os.path.expanduser("~")),
                                              "Bilder (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;Alle Dateien (*)")
        if path and not e.insert_image(path):
            QMessageBox.warning(self, "Bild einfügen", "Die Datei ist kein lesbares Bild.")


    def insert_link(self):
        e = self.current_editor()
        if not e:
            return
        url, ok = EingabeFenster.getText(self, "Hyperlink", "Adresse (z. B. https://…):")
        if ok and url.strip():
            e.insert_link(url.strip())


    def insert_date(self):
        self._ed(lambda e: e.textCursor().insertText(datetime.now().strftime("%d.%m.%Y")))


    def edit_header_footer(self, header: bool):
        t = self.current_tab()
        if not t:
            return
        if not t.editor.web:                                  # Bearbeiten direkt auf der Seite, dazu der Kontext-Reiter
            self.kopffuss_starten(t.editor, header)
            return
        page = t.editor.abschnitt_seite()
        erste = False
        if page.diff_first:
            w, ok = EingabeFenster.getItem(self, "Kopf- und Fußzeile", "Welche Seiten?", ["Erste Seite", "Übrige Seiten"], 0, False)
            if not ok:
                return
            erste = w == "Erste Seite"
        if erste:
            hf = page.first_header if header else page.first_footer
        else:
            hf = page.header if header else page.footer
        d = HeaderFooterDialog(("Kopfzeile" if header else "Fußzeile") + (" (erste Seite)" if erste else ""), hf, self)
        if d.exec():
            if erste:
                if header:
                    page.first_header = d.value()
                else:
                    page.first_footer = d.value()
            elif header:
                page.header = d.value()
            else:
                page.footer = d.value()
            t.editor.page_settings_changed(page)


    def kopffuss_starten(self, editor, header: bool = True):
        """Kopf- oder Fußzeile auf der Seite bearbeiten: Textfeld über dem Rand, Kontext-Reiter „Kopf- und Fußzeile“ eingeblendet und aktiv."""
        from PySide6.QtCore import Qt
        b = editor.kopffuss()
        b.beendet.connect(self._kopffuss_aus, Qt.UniqueConnection)
        if b.starte("kopf" if header else "fuss"):
            self.band.kontext("kopffuss", True, True)


    def _kopffuss_aus(self):
        self.band.kontext("kopffuss", False)


    def insert_page_number(self):
        t = self.current_tab()
        if not t:
            return
        page = t.editor.abschnitt_seite()
        if page.footer.is_empty():
            page.footer = HeaderFooter("{PAGE}", "center")
        elif "{PAGE}" not in page.footer.text:
            page.footer.text += " {PAGE}"
        t.editor.page_settings_changed(page)


