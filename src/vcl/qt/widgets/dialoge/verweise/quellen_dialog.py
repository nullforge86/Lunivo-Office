"""Dialog „Quellen verwalten“: Liste der Quellen mit Neu, Bearbeiten, Löschen und Zitat einfügen. Nur Darstellung; die Daten kommen vom Farmwork."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QListWidget, QListWidgetItem

from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_VERWEIS
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.verweise.quelle_dialog import QuelleDialog


class QuellenDialog(PanelFaehig, QDialog):
    def __init__(self, parent, verweise):
        super().__init__(parent)
        self.verweise = verweise
        self.setWindowTitle("Quellen verwalten")
        self.resize(*GROESSE_FENSTER_VERWEIS)
        v = _spalte("standard", self)
        self.liste = QListWidget(); v.addWidget(self.liste)
        z = FlussLayout()
        for text, fn in (("Neu …", self._neu), ("Bearbeiten …", self._bearb), ("Löschen", self._weg), ("Zitat einfügen", self._zitat)):
            z.addWidget(knopf("standard", text, aktion=fn))
        v.addLayout(z)
        bb = knopfzeile(self, schliessen=True); v.addWidget(bb)
        self._fuellen()

    def _fuellen(self):
        self.liste.clear()
        for q in self.verweise.quellen():
            it = QListWidgetItem(self.verweise.quelle_beschreibung(q)); it.setData(Qt.UserRole, q["tag"]); self.liste.addItem(it)

    def _akt(self):
        it = self.liste.currentItem()
        return next((q for q in self.verweise.quellen() if it and q["tag"] == it.data(Qt.UserRole)), None)

    def _neu(self):
        d = QuelleDialog(self)
        if d.exec():
            self.verweise.quelle_neu(d.ergebnis()); self._fuellen()

    def _bearb(self):
        q = self._akt()
        if q:
            d = QuelleDialog(self, q)
            if d.exec():
                self.verweise.quelle_aendern(q["tag"], d.ergebnis()); self._fuellen()

    def _weg(self):
        q = self._akt()
        if q:
            self.verweise.quelle_entfernen(q["tag"]); self._fuellen()

    def _zitat(self):
        q = self._akt()
        if q:
            self.verweise.zitat_einfuegen(q["tag"]); self.accept()
