"""Vorlagen und Wiederherstellung des Hauptfensters."""
from __future__ import annotations

import os
from datetime import datetime

from PySide6.QtWidgets import QMessageBox

from lunivo_writer.models.report import DocumentIOError
from lunivo_writer.services import file_service as formats
from lunivo_writer.ui.baukasten.speichern_fenster import speicherort_waehlen
from lunivo_writer.ui.document.document_area import DocumentTab


class DateienVorlagenBaustein:
    """Methoden für Dokumentvorlagen und Wiederherstellung."""

    # ==== Vorlagen ==================================================================
    def benutzerdaten(self) -> dict:
        g = self.settings.get
        return {k: g(f"benutzer/{k}", "") or "" for k in ("name", "initialen", "strasse", "plz_ort", "ort", "telefon", "mail")}


    def neu_aus_vorlage(self):
        """Die Seite „Neu“ im Menü: alle Vorlagen als Blätter mit Vorschau."""
        self.backstage_oeffnen("vorlage")


    def neu_aus_wahl(self, art: str, wert) -> None:
        """Legt ein neues Dokument nach der Wahl auf der Seite „Neu“ an: leer, ein Gerüst oder eine Abschrift einer Vorlagendatei."""
        if art == "leer":
            self.new_document()
        elif art == "geruest":
            from lunivo_writer.editor import vorlagen
            from PySide6.QtCore import QDate, QLocale
            self.new_document()
            t = self.current_tab()
            t.title = wert["name"]
            self._update_tab_titles()
            vorlagen.aufbauen(t.editor, wert["zeilen"], self.benutzerdaten(), QLocale("de_DE").toString(QDate.currentDate(), "d. MMMM yyyy"))
        else:
            try:
                geladen = formats.load(wert)
            except DocumentIOError as e:
                QMessageBox.warning(self, "Vorlage", str(e)); return
            tab = DocumentTab(geladen, None, title=os.path.splitext(os.path.basename(wert))[0])
            self._add_tab(tab)
            tab.editor.document().setModified(True)
            self._show_report(geladen.report, "Hinweise zur Vorlage", "beim Öffnen")


    def als_vorlage_speichern(self, ordner: str | None = None):
        """Legt das Blatt als Vorlage ab: im Vorlagenordner oder (``ordner``) in einer seiner Rubriken."""
        t = self.current_tab()
        if not t:
            return
        from lunivo_writer.editor import vorlagen
        ordner = ordner or vorlagen.vorlagenordner(self.settings)
        os.makedirs(ordner, exist_ok=True)
        wahl = speicherort_waehlen(self, "Als Vorlage speichern", os.path.join(ordner, os.path.splitext(t.title)[0] + ".docx"),
                                   [(".docx", formats.SAVE_FILTERS[".docx"])], ".docx")
        if wahl:
            self._write(t, wahl[0], mark_saved=False)


    # ==== Wiederherstellung ================================================================
    def autosave_now(self):
        self.dokumente.sichern(self._doc_tabs())


    def offer_recovery(self):
        open_tokens = {t.token for t in self._doc_tabs()}
        entries = self.dokumente.wiederherstellbar(open_tokens)
        if not entries:
            return
        names = "\n".join(f"• {e.title} ({datetime.fromtimestamp(e.saved_at):%d.%m.%Y %H:%M})" for e in entries)
        box = QMessageBox(QMessageBox.Question, "Wiederherstellung",
                          f"Lunivo Writer wurde nicht ordnungsgemäß beendet. Gesicherte Dokumente:\n\n{names}\n\n"
                          "Wiederherstellen?", QMessageBox.Yes | QMessageBox.No, self)
        box.button(QMessageBox.Yes).setText("Wiederherstellen"); box.button(QMessageBox.No).setText("Verwerfen")
        if box.exec() == QMessageBox.Yes:
            for e in entries:
                try:
                    loaded = self.dokumente.laden(e.docx_path)
                except DocumentIOError:
                    continue
                tab = DocumentTab(loaded, None, title=f"Wiederhergestellt – {e.title}")
                tab.token = e.token
                tab.editor.document().setModified(True)
                self._add_tab(tab)
        else:
            for e in entries:
                self.dokumente.verwerfen(e.token)
