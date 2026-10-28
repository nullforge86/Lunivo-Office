"""Dateien, Vorlagen, Wiederherstellung."""
from __future__ import annotations

import os
from datetime import datetime
from PySide6.QtCore import QTimer, QUrl, Qt
from PySide6.QtGui import QDesktopServices, QFont, QKeySequence
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMenu, QMessageBox
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
                kennwort, ok = QInputDialog.getText(
                    self, "Kennwort", ("Falsches Kennwort. " if e.falsch else "") +
                    f"„{os.path.basename(path)}“ ist geschützt.\nKennwort:", QLineEdit.Password)
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
        if not self.settings.get_bool("sicherheit/markup_oeffnen", True):
            tab.editor.set_markup(False)
        if stile.als_json_neu() != self.settings.get("stile/eigene", ""):       # das Dokument brachte eigene Formatvorlagen mit
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
        if not self._darf_ueberschreiben(tab, path):
            return False
        if formats.ext(path) == ".pdf":
            return self._pdf_schreiben(tab, path)
        try:
            rep = self.dokumente.speichern(path, tab.editor.document(), tab.page, tab.meta)
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


    # Exportoptionen im Fenster „PDF-Datei exportieren“ ↔ gemerkte Einstellung (dieselben Schlüssel wie unter Optionen ▸ Drucken)
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
        """„Als PDF exportieren“: Lunivos Fenster „PDF-Datei exportieren“ (Seitenbereich, Exportoptionen, Berechtigungen)."""
        t = self.current_tab()
        if not t:
            return
        from lunivo_writer.ui.baukasten.pdf_export import pdf_export_fragen

        def exportieren(wahl) -> bool:
            if not self._darf_ueberschreiben(t, wahl.pfad) or not self._pdf_schreiben(t, wahl.pfad, wahl):
                return False
            for feld, (schl, _v) in self.PDF_SCHLUESSEL.items():
                self.settings.set(schl, getattr(wahl, feld))
            self.settings.set("pdf/recht_druck", wahl.druck)
            self.settings.set("pdf/ordner", os.path.dirname(wahl.pfad))
            return True

        e = t.editor
        pdf_export_fragen(self, self.pdf_wahl_start(t), max(1, e.page_count), e.current_page(), e.textCursor().hasSelection(), exportieren)


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
            QMessageBox.critical(self, "PDF-Export fehlgeschlagen", str(e)); return False
        self.statusBar().showMessage(f"PDF gespeichert ({n} Seiten): {path}", 5000)
        if self.settings.get_bool("pdf/oeffnen", False):
            from PySide6.QtCore import QUrl
            from PySide6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))
        return True


    def druck_start(self) -> dict:
        """Letzte Wahl im Druckfenster; Hintergrund, Grafik und Leerseiten teilen sich die Schalter mit den Optionen."""
        g, gb = self.settings.get, self.settings.get_bool
        start = {"hintergrund": gb("drucken/hintergrund", True), "zeichnungen": gb("drucken/zeichnungen", True), "leere": gb("drucken/leere", True),
                 "drucker": g("drucken/dlg_drucker", ""), "kopien": 1, "sortieren": gb("drucken/dlg_sortieren", True),
                 "platzhalter": gb("drucken/dlg_platzhalter", False), "steuerelemente": gb("drucken/dlg_steuerelemente", True),
                 "kommentare": g("drucken/dlg_kommentare", "keine"), "schwarz": gb("drucken/dlg_schwarz", False),
                 "vorschau": gb("drucken/dlg_vorschau", True), "beidseitig": g("drucken/dlg_beidseitig", "aus")}
        return start


    def druck_merken(self, e: dict) -> None:
        for k in ("hintergrund", "zeichnungen", "leere"):
            self.settings.set(f"drucken/{k}", e[k])
        for k in ("drucker", "sortieren", "platzhalter", "steuerelemente", "kommentare", "schwarz", "vorschau", "beidseitig"):
            self.settings.set(f"drucken/dlg_{k}", e[k])


    def druck_vorschau(self, t):
        from lunivo_writer.editor.druck import optionen_aus, vorschau_bild

        def bilder(nummern, ein):
            opt = optionen_aus(self.druckoptionen(), ein, t.editor.noten)
            return vorschau_bild(t.editor.document(), t.page, opt, t.editor.noten, nummern)
        return bilder


    def _druck_args(self, t) -> dict:
        from lunivo_writer.editor.pagination import seitenzahl
        start = self.druck_start()
        if self.settings.get("drucken/vorgabe", "Alle Seiten") == "Aktuelle Seite":
            start.update(bereich="seiten", seiten_text=str(t.editor.current_page()))
        ps = t.page
        return dict(seiten=seitenzahl(t.editor.document(), ps, t.editor.noten), papier_mm=(ps.width_mm, ps.height_mm), quer=bool(ps.landscape),
                    start=start, auswahl=t.editor.textCursor().hasSelection(), vorschau=self.druck_vorschau(t))


    def druck_ansicht(self, t, parent=None):
        """Das Druckfenster ohne Knopfzeile (Menü ▸ Drucken, zweite Spalte)."""
        from lunivo_writer.ui.baukasten.druck_dialog import DruckAnsicht
        a = DruckAnsicht(parent=parent, **self._druck_args(t))
        a.eigenschaften.connect(lambda name: self._drucker_eigenschaften(a, name))
        return a


    def print_dialog(self):
        """Drucken (Strg+P, Schnellzugriff, Druckvorschau): die Seite „Drucken“ im Menü, kein eigenes Fenster."""
        if self.current_tab():
            self.backstage_oeffnen("drucken")


    def druckfenster(self):
        """Dasselbe als eigenes Fenster (für Aufrufer ohne Menü)."""
        t = self.current_tab()
        if not t:
            return
        from lunivo_writer.ui.baukasten.druck_dialog import DruckDialog
        dlg = DruckDialog(self, hilfe=self.druck_hilfe, **self._druck_args(t))
        dlg.ansicht.eigenschaften.connect(lambda name: self._drucker_eigenschaften(dlg.ansicht, name))
        if not dlg.exec():
            return
        self.drucke_nach_wahl(t, dlg.ergebnis())


    def druck_hilfe(self):
        QMessageBox.information(self, "Drucken", "Links sehen Sie das Blatt, wie es gedruckt wird. Rechts wählen Sie Drucker, Seiten, Kopien und Papier; "
                                "auf „Lunivo-Office“ stehen die Inhalte des Dokuments.")


    def drucke_nach_wahl(self, t, e: dict) -> None:
        """Druckt das Blatt `t` nach der Wahl `e` (Druckfenster oder Menü ▸ Drucken)."""
        from PySide6.QtPrintSupport import QPrinterInfo
        from lunivo_writer.editor.druck import drucken
        self.druck_merken(e)
        info = QPrinterInfo.printerInfo(e["drucker"]) if e["drucker"] else QPrinterInfo()
        pr = QPrinter(info, QPrinter.HighResolution if self.settings.get_bool("drucken/hoch", True) else QPrinter.ScreenResolution) \
            if not info.isNull() else self._neuer_drucker()
        if not e["drucker"]:                                           # kein Drucker eingerichtet: das Fenster des Systems übernimmt
            if not QPrintDialog(pr, self).exec():
                return
        self._vor_dem_drucken(t)
        n = drucken(pr, t.editor.document(), t.page, self.druckoptionen(), e, t.editor.noten)
        self.statusBar().showMessage(f"An den Drucker gesendet ({n} Blatt)." if n else "Keine Seiten zum Drucken.", 4000)


    def _drucker_eigenschaften(self, dlg, name: str) -> None:
        from PySide6.QtPrintSupport import QPrinterInfo
        pr = QPrinter(QPrinterInfo.printerInfo(name))
        sys_dlg = QPrintDialog(pr, self)
        sys_dlg.setOption(QPrintDialog.PrintPageRange, False)
        if sys_dlg.exec():
            dlg.drucker_setzen(pr.copyCount(), {QPrinter.DuplexLongSide: "lang", QPrinter.DuplexShortSide: "kurz"}.get(pr.duplex(), "aus"))


    def print_preview(self):
        t = self.current_tab()
        if not t:
            return
        from lunivo_writer.editor.druck import Zwischenseiten, optionen_aus
        from lunivo_writer.ui.baukasten.druckvorschau import DruckVorschau
        opt = optionen_aus(self.druckoptionen(), self.druck_start(), t.editor.noten)
        dlg = DruckVorschau(self, Zwischenseiten(t.editor.document(), t.page, opt, t.editor.noten))
        dlg.drucken.connect(lambda: QTimer.singleShot(0, self.print_dialog))
        dlg.showMaximized()
        dlg.exec()


    def ausgabe_ppi(self) -> int:
        """Standard-Ausgabeziel: Auflösung für „Als Bild exportieren“."""
        try:
            return int(str(self.settings.get("ausgabe/ppi", "150")).split()[0])
        except (ValueError, IndexError):
            return 150


    def druckoptionen(self) -> dict:
        return {"umgekehrt": self.settings.get_bool("drucken/umgekehrt", False),
                "duplex": self.settings.get("drucken/duplex", "alle"),
                "hintergrund": self.settings.get_bool("drucken/hintergrund", True),
                "leere": self.settings.get_bool("drucken/leere", True),
                "hervorhebungen": self.settings.get_bool("drucken/hervorhebungen", True),
                "textmarken": self.settings.get_bool("drucken/textmarken", False),
                "textgrenzen": self.settings.get_bool("drucken/textgrenzen", False),
                "zuschnitt": self.settings.get_bool("drucken/zuschnitt", False),
                "silbenfarben": self._silben_fuer_druck(),
                "versteckt": self.settings.get_bool("drucken/versteckt", False),
                "felder_code": self.settings.get_bool("drucken/felder_code", False),
                "zeichnungen": self.settings.get_bool("drucken/zeichnungen", True),
                "balken": self.settings.get("aenderungen/balken", "links"),
                "notenlinks": self.settings.get_bool("pdf/notenlinks", True),
                "blasen": self._blasen_fuer_druck(),
                "nur_formular": self.settings.get_bool("drucken/nur_formular", False)}


    def _blasen_fuer_druck(self):
        from lunivo_writer.editor import sprechblasen as SB
        e = self.current_editor()
        k = SB.konfig_lesen(self.settings)
        if e is None or not self.settings.get_bool("sprechblasen/drucken", False) or not SB.aktiv(k):
            return None
        if not e.kommentare and not (k["verwenden"] == "Immer" and e.aenderungen()):
            return None
        return {"konfig": k, "kommentare": dict(e.kommentare)}


    def _silben_fuer_druck(self):
        from lunivo_writer.editor import silbenfarben as S
        k = S.konfig_lesen(self.settings)
        return dict(k, nur_absatz=False) if k["an"] and k["drucken"] else None


    def _neuer_drucker(self):
        return QPrinter(QPrinter.HighResolution if self.settings.get_bool("drucken/hoch", True) else QPrinter.ScreenResolution)


    def _vor_dem_drucken(self, tab):
        """„Felder vor dem Drucken aktualisieren“: Verzeichnisse neu rechnen."""
        if self.settings.get_bool("drucken/felder", True):
            from lunivo_writer.editor.verzeichnis import verzeichnis_aktualisieren
            verzeichnis_aktualisieren(tab.editor)


    def reiter_menue(self, index: int, pos) -> None:
        """Kontextmenü am Dokumentreiter."""
        w = self.tabs.widget(index) if index >= 0 else None
        if not isinstance(w, DocumentTab):
            return
        m = QMenu(self)
        m.addAction("Schließen", lambda: self.close_tab(index))
        m.addAction("Andere schließen", lambda: self._reiter_schliessen(w, nur_andere=True))
        m.addAction("Alle schließen", lambda: self._reiter_schliessen(w, nur_andere=False))
        m.addSeparator()
        m.addAction("Speichern", lambda: (self.tabs.setCurrentIndex(index), self._save_tab(w)))
        pfad = m.addAction("Pfad kopieren", lambda: QApplication.clipboard().setText(w.path))
        ordner = m.addAction("Ordner öffnen", lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(w.path))))
        pfad.setEnabled(bool(w.path)); ordner.setEnabled(bool(w.path))
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
        tabelle = [("F3", b.schnellbaustein), ("F4", b.vorlesen), ("F5", self.toggle_sidebar), ("F6", b.welcheHilfe),
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
