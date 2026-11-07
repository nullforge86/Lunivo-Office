"""Dateien, Vorlagen, Wiederherstellung."""
from __future__ import annotations

import os
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices, QKeySequence
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.services import file_service as formats
from lunivo_writer.services import sicher_schreiben
from lunivo_writer.models.report import DocumentIOError
from lunivo_writer.editor.pagination import export_pdf
from lunivo_writer.ui.document.document_area import DocumentTab
from lunivo_writer.ui.baukasten.speichern_fenster import speicherort_waehlen
from lunivo_writer.ui.hauptfenster.dateien_oeffnen import DateienOeffnenBaustein
from lunivo_writer.ui.hauptfenster.dateien_drucken import DateienDruckenBaustein
from lunivo_writer.ui.hauptfenster.dateien_vorlagen import DateienVorlagenBaustein
from lunivo_writer.ui.hauptfenster.dateien_speichern import DateienSpeichernBaustein


class DateienBaustein(DateienOeffnenBaustein, DateienVorlagenBaustein, DateienSpeichernBaustein, DateienDruckenBaustein):
    """Dateien, Vorlagen, Wiederherstellung. Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``)."""


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
            n = sicher_schreiben.schreiben(path, erzeugen, endung=".pdf")
        except Exception as e:  # PDF-Ausgabe darf das Programm nicht beenden
            QMessageBox.critical(self, "PDF-Export fehlgeschlagen", f"Die PDF-Datei wurde nicht erstellt.\n\nGrund: {e}\n\nWählen Sie einen anderen Ordner oder Dateinamen."); return False
        self.statusBar().showMessage(f"PDF gespeichert ({n} Seiten): {path}", 5000)
        if self.settings.get_bool("pdf/oeffnen", False):
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        return True


    def reiter_menue(self, index: int, pos) -> None:
        """Kontextmenü am Dokumentreiter."""
        w = self.tabs.widget(index) if index >= 0 else None
        if not isinstance(w, DocumentTab):
            return
        m = MenueListe(self)
        m.eintrag("Schließen", lambda: self.close_tab(index))
        m.eintrag("Andere schließen", lambda: self._reiter_schliessen(w, nur_andere=True))
        m.eintrag("Alle schließen", lambda: self._reiter_schliessen(w, nur_andere=False))
        m.trenner()
        m.eintrag("Speichern", lambda: (self.tabs.setCurrentIndex(index), self._save_tab(w)))
        m.eintrag("Pfad kopieren", lambda: QApplication.clipboard().setText(w.path), aktiv=bool(w.path))
        m.eintrag("Ordner öffnen", lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(w.path))), aktiv=bool(w.path))
        m.exec(pos)


    def _reiter_schliessen(self, behalten, nur_andere: bool) -> None:
        for i in range(self.tabs.count() - 1, -1, -1):
            t = self.tabs.widget(i)
            if isinstance(t, DocumentTab) and not (nur_andere and t is behalten):
                if not self.close_tab(i):
                    return


    def close_tab(self, index: int) -> bool:
        w = self.tabs.widget(index)
        if not isinstance(w, DocumentTab):
            return False
        if w.is_modified():
            self.tabs.setCurrentIndex(index)
            box = QMessageBox(QMessageBox.Question, "Ungespeicherte Änderungen",
                              f"Möchten Sie die Änderungen an „{w.title}“ speichern?",
                              QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel, self)
            box.button(QMessageBox.Save).setText("Speichern")
            box.button(QMessageBox.Discard).setText("Nicht speichern")
            box.button(QMessageBox.Cancel).setText("Abbrechen")
            r = box.exec()
            if r == QMessageBox.Cancel:
                return False
            if r == QMessageBox.Save and not self._save_tab(w):
                return False
        self.dokumente.verwerfen(w.token)
        self.tabs.removeTab(index)
        w.deleteLater()
        self._refresh_ui()
        return True


    def _zusatz_kuerzel(self):
        """Kürzel ohne eigene Aktion (Tabelle in windows/kuerzel.py zeigt sie in der Hilfe)."""
        from PySide6.QtGui import QShortcut
        b = self.befehle
        tabelle = [("F3", b.schnellbaustein), ("F4", b.vorlesen), ("F5", self.toggle_sidebar), ("F6", b.welcheHilfe), ("F10", self.zum_band_springen),
                   ("F7", lambda: self.assistant.pruefen(True)), ("F8", b.kiKorrektur),
                   ("Ctrl++", b.groesser), ("Ctrl+-", b.kleiner), ("Ctrl+0", b.normal),
                   ("Ctrl+D", b.schriftartMehr), ("Ctrl+Alt+V", b.inhalteEinfuegen), ("Ctrl+Alt+T", b.einfuegenUnformatiert),
                   ("Ctrl+Alt+F", b.fussnote), ("Ctrl+Alt+D", b.endnote),
                   ("Ctrl+Shift+H", b.ausblenden), ("Ctrl+Tab", lambda: self._tab_weiter(1)), ("Ctrl+Shift+Tab", lambda: self._tab_weiter(-1))]
        self._kuerzel = []
        for taste, fn in tabelle:
            sc = QShortcut(QKeySequence(taste), self)
            sc.setContext(Qt.WindowShortcut)
            sc.activated.connect(fn)
            self._kuerzel.append(sc)


    def _tab_weiter(self, d: int):
        n = self.tabs.count()
        if n > 1:
            self.tabs.setCurrentIndex((self.tabs.currentIndex() + d) % n)


