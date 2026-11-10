"""Mehrere Hauptfenster: Liste, Neues Fenster, Anordnen, Fensterliste, Schließen."""
from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QApplication, QMenu, QMessageBox

from lunivo_writer.ui.document.dokumentfenster.document_area import DocumentTab

if TYPE_CHECKING:
    from lunivo_writer.ui.main_window import MainWindow


class FensterVerwaltungMixin:
    """Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``)."""

    # ==== Fenster ====================================================================
    @staticmethod
    def alle_fenster() -> list["MainWindow"]:
        from lunivo_writer.ui.main_window import MainWindow
        return [w for w in QApplication.topLevelWidgets() if isinstance(w, MainWindow) and w.isVisible()]

    def neues_fenster(self):
        """Das aktuelle Dokument in einem zweiten Fenster öffnen (eigene Kopie, keine Synchronisation)."""
        t = self.current_tab()
        if t is None:
            w = type(self)(self.settings); w.show(); return w
        if t.is_modified() or not t.path:
            r = QMessageBox.question(self, "Neues Fenster",
                                     "Das neue Fenster zeigt die gespeicherte Datei als eigene Kopie. Änderungen werden nicht zwischen "
                                     "den Fenstern abgeglichen.\n\nJetzt speichern und das Fenster öffnen?")
            if r != QMessageBox.Yes or not self.save():
                return None
        w = type(self)(self.settings)
        w.show()
        w.open_path(t.path)
        return w

    def fenster_anordnen(self, art: str):
        fenster = self.alle_fenster()
        if len(fenster) < 2:
            self.statusBar().showMessage("Zum Anordnen werden mindestens zwei Fenster gebraucht (Ansicht ▸ Neues Fenster).", 5000)
            return
        r = (self.screen() or QApplication.primaryScreen()).availableGeometry()
        n = len(fenster)
        if art == "nebeneinander":
            spalten, zeilen = n, 1
        elif art == "untereinander":
            spalten, zeilen = 1, n
        else:
            spalten = int(n ** 0.5 + 0.999); zeilen = (n + spalten - 1) // spalten
        bw, bh = r.width() // spalten, r.height() // zeilen
        for i, f in enumerate(fenster):
            f.showNormal()
            f.setGeometry(r.x() + (i % spalten) * bw, r.y() + (i // spalten) * bh, bw, bh)

    def fensterliste_menue(self) -> QMenu:
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for f in self.alle_fenster():
            for t in f._doc_tabs():
                m.eintrag(t.title + ("  (dieses Fenster)" if f is self else ""),
                          lambda f=f, t=t: (f.raise_(), f.activateWindow(), f.tabs.setCurrentWidget(t)))
        if m.isEmpty():
            m.eintrag("Keine Dokumente geöffnet", aktiv=False)
        return m

    def closeEvent(self, ev):
        for i in range(self.tabs.count() - 1, -1, -1):
            if isinstance(self.tabs.widget(i), DocumentTab) and not self.close_tab(i):
                ev.ignore(); return
        self.settings.set("window/geometry", self.saveGeometry())
        ev.accept()
