"""Reiterverwaltung und zusätzliche Tastenkürzel für das Hauptfenster."""
from __future__ import annotations

import os
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices, QKeySequence
from PySide6.QtWidgets import QApplication, QMessageBox
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.ui.document.dokumentfenster.document_area import DocumentTab


class DateienReiterBaustein:
    """Kontextmenüs, Schließen von Dokumentreitern und Reiter-Tastenkürzel."""

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
