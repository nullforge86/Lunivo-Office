"""Aktionen zum Dokumentschutz (Überprüfen ▸ Bearbeitung einschränken): Seitenleistenfenster öffnen und den Schutz am Dokumentfenster setzen."""
from __future__ import annotations

from lunivo_writer.oberflaeche.funktionen.ueberpruefen.schutz_dialog import SchutzDialog


class SchutzAktionen:
    def bearbeitungEinschraenken(self, k=None):
        """Seitenleiste „Bearbeitung einschränken“: Schreibgeschützt, nur nachverfolgte Änderungen oder nur Kommentare."""
        t = self.w.current_tab()
        if t is None:
            return
        d = SchutzDialog(self.w, getattr(t, "schutz", None))
        if d.exec():
            self.schutz_setzen(t, d.ergebnis())

    def schutz_setzen(self, t, art: str | None) -> None:
        t.schutz = art
        t.gesperrt = art in ("lesen", "kommentare")       # Kommentare gehen auch im schreibgeschützten Text
        t.editor.setReadOnly(t.gesperrt or self.w.lesemodus)
        if art == "aenderungen":
            t.editor.set_verfolgen(True)
        text = {None: "Dokumentschutz beendet.", "lesen": "Dokument ist schreibgeschützt.",
                "aenderungen": "Alle Änderungen werden nachverfolgt.", "kommentare": "Nur Kommentare sind erlaubt."}[art]
        self.w.statusBar().showMessage(text, 5000)
        self.w.band.aktualisieren()
