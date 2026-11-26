"""Dialog „Textmarke“: Namen eintragen, hinzufügen, löschen, hingehen. Nur Darstellung; alles Fachliche fragt der Dialog beim Farmwork."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QListWidget, QMessageBox

from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig


class TextmarkeDialog(PanelFaehig, QDialog):
    def __init__(self, parent, verweise):
        super().__init__(parent)
        self.verweise = verweise
        self.setWindowTitle("Textmarke")
        v = _spalte("standard", self)
        self.name = zeilenfeld("frei", platzhalter="Name (Buchstaben, Ziffern, _ ; beginnt mit Buchstaben)")
        v.addWidget(self.name)
        self.liste = QListWidget(); self.liste.itemDoubleClicked.connect(lambda _: self._gehe())
        v.addWidget(self.liste)
        z = FlussLayout()
        for text, fn in (("Hinzufügen", self._add), ("Löschen", self._del), ("Gehe zu", self._gehe)):
            z.addWidget(knopf("standard", text, aktion=fn))
        v.addLayout(z)
        bb = knopfzeile(self, schliessen=True); v.addWidget(bb)
        self._fuellen()

    def _fuellen(self):
        self.liste.clear()
        for name in self.verweise.lesezeichen_namen():
            self.liste.addItem(name)

    def _add(self):
        n = self.name.text().strip()
        if not self.verweise.lesezeichen_name_gueltig(n):
            QMessageBox.information(self, "Textmarke", "Der Name muss mit einem Buchstaben beginnen und darf nur Buchstaben, Ziffern und _ enthalten.")
            return
        if not self.verweise.lesezeichen_setzen(n):
            QMessageBox.information(self, "Textmarke", "Bitte Text markieren oder in ein Wort klicken.")
            return
        self._fuellen()

    def _del(self):
        it = self.liste.currentItem()
        if it:
            self.verweise.lesezeichen_loeschen(it.text()); self._fuellen()

    def _gehe(self):
        it = self.liste.currentItem()
        if it:
            self.verweise.lesezeichen_gehe(it.text())
