"""Speicherfunktionen für das Hauptfenster."""
from __future__ import annotations

import os
from PySide6.QtWidgets import QMessageBox
from lunivo_writer.services import file_service as formats
from lunivo_writer.services import sicher_schreiben
from lunivo_writer.models.report import DocumentIOError
from lunivo_writer.ui.document.document_area import DocumentTab
from lunivo_writer.ui.baukasten.dokument.speichern_fenster import speicherort_waehlen


class DateienSpeichernBaustein:
    """Speichern und Exportieren von Dokumentdateien."""

    def save(self) -> bool:
        t = self.current_tab()
        return self._save_tab(t) if t else False


    def _save_tab(self, tab: DocumentTab) -> bool:
        if tab.path is None or formats.ext(tab.path) not in (".docx", ".odt", ".rtf", ".txt"):
            return self._save_tab_as(tab)
        return self._write(tab, tab.path)


    def save_as(self) -> bool:
        t = self.current_tab()
        return self._save_tab_as(t) if t else False


    def save_as_format(self, ext: str) -> bool:
        """Speichern unter mit vorgewähltem Dateiformat (Untermenü „Speichern unter ▸“) — dasselbe Fenster wie „Speichern unter“."""
        t = self.current_tab()
        return self._save_tab_as(t, ext) if t else False


    # Reihenfolge der Dateitypen im Speichern-Fenster
    SPEICHER_FORMATE = (".docx", ".odt", ".rtf", ".txt", ".pdf")


    def _ask_path(self, tab: DocumentTab, title: str, only: str | None = None) -> str | None:
        """Das eine Speichern-Fenster: Dateiname und Dateityp. `only` wählt den Dateityp vor, alle anderen bleiben wählbar."""
        folder = os.path.dirname(tab.path) if tab.path else (self.settings.get("speichern/ordner", "") or
                                                             self.settings.get("last_dir", os.path.expanduser("~")))
        base = os.path.splitext(tab.title)[0] or "Unbenannt"
        default = only or self.settings.get("speichern/standard", ".docx")
        if default not in self.SPEICHER_FORMATE:
            default = ".docx"
        filter_von = lambda e: formats.PDF_FILTER if e == ".pdf" else formats.SAVE_FILTERS[e]
        # Lunivos eigenes Fenster statt des Systemdialogs: Der Dateiauswahldialog des Desktops (Portal/Dateimanager)
        # blendet die Dateityp-Auswahl je nach System aus — hier stehen Dateiname und Dateityp immer sichtbar da.
        wahl = speicherort_waehlen(self, title, os.path.join(folder, base + default),
                                   [(e, filter_von(e)) for e in self.SPEICHER_FORMATE], default)
        if not wahl:
            return None
        path, gewaehlt = wahl
        e = formats.ext(path)
        if gewaehlt and e in self.SPEICHER_FORMATE and e != gewaehlt:  # der gewählte Dateityp gilt, auch wenn der Name noch die alte Endung trägt
            path = path[: -len(e)]
            e = ""
        if e not in self.SPEICHER_FORMATE:                       # ohne oder mit fremder Endung: die des gewählten Dateityps
            path += gewaehlt or default
        return path


    def _save_tab_as(self, tab: DocumentTab, only: str | None = None) -> bool:
        path = self._ask_path(tab, "Speichern unter", only=only)
        if not path or not self._write(tab, path):
            return False
        if formats.ext(path) == ".pdf":                        # PDF ist eine Ausgabe; das Dokument bleibt bei seiner Datei
            return True
        tab.set_path(path)
        self.settings.add_recent(path)
        self._update_tab_titles()
        return True


    def _darf_ueberschreiben(self, tab: DocumentTab, path: str) -> bool:
        """Fragt nach, bevor eine Datei überschrieben wird, die außerhalb von Lunivo geändert wurde oder offen ist."""
        name = os.path.basename(path)
        bekannt = getattr(tab, "datei_stand", None)
        jetzt = sicher_schreiben.stand(path)
        if tab.path and os.path.abspath(tab.path) == os.path.abspath(path) and bekannt and jetzt and jetzt != bekannt:
            box = QMessageBox(QMessageBox.Warning, "Datei wurde geändert",
                              f"„{name}“ wurde seit dem Öffnen oder letzten Speichern außerhalb von Lunivo geändert "
                              "(z. B. durch ein anderes Programm oder die Synchronisierung eines Cloud-Ordners).\n\n"
                              "Beim Überschreiben gehen diese Änderungen verloren. Die bisherige Fassung kommt in die Sicherungskopien.",
                              QMessageBox.Cancel, self)
            ueber = box.addButton("Trotzdem überschreiben", QMessageBox.DestructiveRole)
            box.setDefaultButton(QMessageBox.Cancel)
            box.exec()
            if box.clickedButton() is not ueber:
                return False
        programm = sicher_schreiben.fremd_geoeffnet(path) if jetzt else None
        if programm:
            box = QMessageBox(QMessageBox.Warning, "Datei ist geöffnet",
                              f"„{name}“ ist gerade in {programm} geöffnet. Speichert es die Datei danach, überschreibt es diese Fassung.",
                              QMessageBox.Cancel, self)
            weiter = box.addButton("Trotzdem speichern", QMessageBox.AcceptRole)
            box.setDefaultButton(QMessageBox.Cancel)
            box.exec()
            if box.clickedButton() is not weiter:
                return False
        return True


    def _write(self, tab: DocumentTab, path: str, mark_saved: bool = True) -> bool:
        gesehen = sicher_schreiben.stand(path)               # was der Benutzer jetzt vor sich hat; ändert es sich bis zum Schreiben, meldet es die Sperre
        if not self._darf_ueberschreiben(tab, path):
            return False
        if formats.ext(path) == ".pdf":
            return self._pdf_schreiben(tab, path)
        try:
            rep = self.dokumente.speichern(path, tab.editor.document(), tab.page, tab.meta, erwartet=(gesehen,))
        except DocumentIOError as e:
            QMessageBox.critical(self, "Speichern fehlgeschlagen", f"Das Dokument wurde nicht gespeichert.\n\nGrund: {e}\n\nWählen Sie „Speichern unter“ und einen anderen Ordner, oder prüfen Sie den Schreibschutz."); return False
        if mark_saved:
            tab.editor.document().setModified(False)
            self.dokumente.verwerfen(tab.token)
            tab.datei_stand = sicher_schreiben.stand(path)
        self.statusBar().showMessage(f"Gespeichert: {path}", 4000)
        self._show_report(rep, "Hinweise zum Speichern", "beim Speichern")
        return True


    def save_copy(self):
        self.export_as(".docx", title="Kopie speichern")


    def export_as(self, ext: str, title: str | None = None):
        t = self.current_tab()
        if not t:
            return
        path = self._ask_path(t, title or "Exportieren", only=ext)
        if path:
            self._write(t, path, mark_saved=False)
