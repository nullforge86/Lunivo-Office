"""Öffnen und Anlegen von Dokumenten im Hauptfenster."""
from __future__ import annotations

import os

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QMessageBox

from lunivo_writer.editor.text import stile
from lunivo_writer.modelle.seite import PageSettings
from lunivo_writer.modelle.bericht import DocumentIOError, IOReport, PasswortNoetig
from lunivo_writer.dienste import datei_dienst as formats
from lunivo_writer.dienste import sicher_schreiben
from lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster import EingabeFenster
from lunivo_writer.oberflaeche.dokument.dokumentfenster.dokument_bereich import DocumentTab


class DateienOeffnenBaustein:
    """Methoden zum Erstellen und Öffnen von Dokumenten."""

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
        from lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster import datei_waehlen
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
        from lunivo_writer.editor.objekte import frei_objekt as FO
        FO.kette_aktualisieren(tab.editor)                         # verknüpfte Textfelder: der Text läuft von Feld zu Feld
        tab.editor.document().setModified(False)
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


