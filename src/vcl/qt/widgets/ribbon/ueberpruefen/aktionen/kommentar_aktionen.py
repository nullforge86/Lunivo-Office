"""Aktionen der Kommentar-Knöpfe im Reiter „Überprüfen“: Eingabefeld öffnen, durchgehen, löschen. Die Befehle liegen im Farmwork."""
from __future__ import annotations

from PySide6.QtWidgets import QMessageBox

from vcl.qt.widgets.dialoge.dokument.eingabe_fenster import EingabeFenster


class KommentarAktionen:
    def _text_abfragen(self, titel, frage, vorgabe=""):
        t, ok = EingabeFenster.getMultiLineText(self.w, titel, frage, vorgabe)
        return t.strip() if ok and t.strip() else None

    def kommentar(self, k=None):
        """Neuer Kommentar wie in der Vorlage: das Feld „Kommentare“ links öffnet sich mit dem Eingabefeld — Knopf und Seitenleiste
        arbeiten mit denselben Kommentaren des Dokuments. Ohne Markierung hängt er am Wort, sonst an der Schreibmarke."""
        fw = self._kommentare()
        if fw is not None and fw.neu_erlaubt(self._schutz_wert()):
            self.w.navigation._neu_zeigen()

    def kommentarWeiter(self, k=None):
        fw = self._kommentare()
        if fw is not None:
            fw.springen(1)

    def kommentarZurueck(self, k=None):
        fw = self._kommentare()
        if fw is not None:
            fw.springen(-1)

    def kommentarWeg(self, k=None):
        fw = self._kommentare()
        if fw is not None:
            fw.am_zeiger_loeschen()
        else:
            self.w.statusBar().showMessage("Der Zeiger steht in keinem Kommentar.", 4000)

    def kommentareAlleWeg(self, k=None):
        fw = self._kommentare()
        if fw is not None and fw.vorhanden() and QMessageBox.question(
                self.w, "Kommentare", "Alle Kommentare im Dokument löschen?") == QMessageBox.Yes:
            fw.alle_loeschen()
