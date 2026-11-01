"""Dateien, Vorlagen, Wiederherstellung."""
from __future__ import annotations

import os
from datetime import datetime
from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QDesktopServices, QFont, QKeySequence
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import QApplication, QLineEdit, QMenu, QMessageBox, QWidget
from lunivo_writer.ui.baukasten.eingabe_fenster import EingabeFenster
from lunivo_writer.editor import stile
from lunivo_writer.services import file_service as formats
from lunivo_writer.services import sicher_schreiben
from lunivo_writer.models.report import DocumentIOError, IOReport, PasswortNoetig
from lunivo_writer.models.page import PageSettings
from lunivo_writer.editor.pagination import export_pdf
from lunivo_writer.ui.document.document_area import DocumentTab
from lunivo_writer.ui.baukasten.speichern_fenster import speicherort_waehlen


class DateienBaustein:
    """Dateien, Vorlagen, Wiederherstellung. Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``)."""

    # ==== Dateien ======================================================================
    def new_document(self):
        tab = DocumentTab()
        from PySide6.QtGui import QTextDocument
        d = QTextDocument()
        f = QFont(self.settings.get("standard/schrift", "Liberation Sans"))
        f.setPointSizeF(float(self.settings.get("standard/groesse", 11)))
        d.setDefaultFont(f)
        tab.editor.set_document_and_page(d, PageSettings())
        self._add_tab(tab)

    def _add_tab(self, tab: DocumentTab):
        self._connect_tab(tab)
        tab.editor.setReadOnly(self.lesemodus)
        i = self.tabs.addTab(tab, self._tab_title(tab))
        self.tabs.setCurrentIndex(i)
        self._update_tab_titles()
        tab.editor.setFocus()

    def open_dialog(self):
        start = self.settings.get("last_dir", os.path.expanduser("~"))
        from lunivo_writer.ui.baukasten.speichern_fenster import datei_waehlen
        paths = datei_waehlen(self, "Öffnen", start, formats.OPEN_FILTER, mehrere=True)
        for p in paths:
            self.open_path(p)

    def open_path(self, path: str) -> bool:
        path = os.path.abspath(path)
        for i, t in enumerate(self._doc_tabs()):
            if t.path == path:
                self.tabs.setCurrentWidget(t); return True
        kennwort = None
        while True:
            try:
                loaded = self.dokumente.laden(path, kennwort)
                break
            except PasswortNoetig as e:
                kennwort, ok = EingabeFenster.getText(
                    self, "Kennwort", ("Falsches Kennwort. " if e.falsch else "") +
                    f"„{os.path.basename(path)}“ ist geschützt.\nKennwort:", kennwort=True)
                if not ok:
                    return False
                continue
            except DocumentIOError as e:
                loaded, fehler = None, e
                break
        if loaded is None:
            QMessageBox.warning(self, "Öffnen nicht möglich", f"{os.path.basename(path)}\n\n{fehler}")
            self.dokumente.vergessen(path)
            return False
        tab = DocumentTab(loaded, path)
        tab.datei_stand = sicher_schreiben.stand(path)
        self._add_tab(tab)
        from lunivo_writer.editor import frei_objekt as FO
        FO.kette_aktualisieren(tab.editor)
        tab.editor.document().setModified(False)
        if not self.settings.get_bool("sicherheit/markup_oeffnen", True):
            tab.editor.set_markup(False)
        if stile.als_json_neu() != self.settings.get("stile/eigene", ""):
            self.settings.set("stile/eigene", stile.als_json_neu())
            getattr(self.band, "stile_aktualisieren", lambda: None)()
        self.dokumente.gelesen(path)
        self._show_report(loaded.report, f"Hinweise zu „{os.path.basename(path)}“", "beim Öffnen")
        return True

    def _show_report(self, rep: IOReport, title: str, when: str):
        if rep:
            QMessageBox.information(self, title,
                                    f"Nicht alles konnte {when} übernommen werden:\n\n• " + "\n• ".join(rep.warnings))

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

    SPEICHER_FORMATE = (".docx", ".odt", ".rtf", ".txt", ".pdf")

    def _ask_path(self, tab: DocumentTab, title: str, only: str | None = None) -> str | None:
        folder = os.path.dirname(tab.path) if tab.path else (self.settings.get("speichern/ordner", "") or
                                                             self.settings.get("last_dir", os.path.expanduser("~")))
        base = os.path.splitext(tab.title)[0] or "Unbenannt"
        default = only or self.settings.get("speichern/standard", ".docx")
        if default not in self.SPEICHER_FORMATE:
            default = ".docx"
        filter_von = lambda e: formats.PDF_FILTER if e == ".pdf" else formats.SAVE_FILTERS[e]
        wahl = speicherort_waehlen(self, title, os.path.join(folder, base + default),
                                  [(e, filter_von(e)) for e in self.SPEICHER_FORMATE], default)
        if not wahl:
            return None
        path, gewaehlt = wahl
        e = formats.ext(path)
        if gewaehlt and e in self.SPEICHER_FORMATE and e != gewaehlt:
            path = path[: -len(e)]
            e = ""
        if e not in self.SPEICHER_FORMATE:
            path += gewaehlt or default
        return path

    def _save_tab_as(self, tab: DocumentTab, only: str | None = None) -> bool:
        path = self._ask_path(tab, "Speichern unter", only=only)
        if not path or not self._write(tab, path):
            return False
        if formats.ext(path) == ".pdf":
            return True
        tab.set_path(path)
        self.settings.add_recent(path)
        self._update_tab_titles()
        return True

    def _darf_ueberschreiben(self, tab: DocumentTab, path: str) -> bool:
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
        if not self._darf_ueberschreiben(tab, path):
            return False
        if formats.ext(path) == ".pdf":
            return self._pdf_schreiben(tab, path)
        try:
            erwarteter_stand = getattr(tab, "datei_stand", None)
            rep = self.dokumente.speichern(path, tab.editor.document(), tab.page, tab.meta, erwarteter_stand=erwarteter_stand)
        except DocumentIOError as e:
            QMessageBox.critical(self, "Speichern fehlgeschlagen", str(e)); return False
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

    def _pdf_schreiben(self, t: DocumentTab, path: str, wahl=None) -> bool:
        from lunivo_writer.services import pdf_export as PE
        if wahl is None:
            wahl = self.pdf_wahl_start(t); wahl.pfad = path
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
            n = sicher_schreiben.schreiben(path, erzeugen, endung=".pdf", erwarteter_stand=getattr(t, "datei_stand", None))
        except Exception as e:
            QMessageBox.critical(self, "PDF-Export fehlgeschlagen", str(e)); return False
        self.statusBar().showMessage(f"PDF gespeichert ({n} Seiten): {path}", 5000)
        if self.settings.get_bool("pdf/oeffnen", False):
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        return True
