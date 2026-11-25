"""Dialog „Etiketten“: Bogen, Aufschrift und ob überall dasselbe steht."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QPlainTextEdit

from lunivo_writer.farmwork.funktionen.sendungen.formate import etiketten_boegen
from lunivo_writer.oberflaeche.baukasten.basis.mass import HOEHE_TEXT_NORMAL
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FormularGitter
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.funktionen.sendungen.dialog_hilfen import hinweis, ok_zeile


class EtikettenDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Etiketten")
        f = FormularGitter(self)
        f.breit(hinweis("Ein Bogen wird angelegt. Steht überall dasselbe, kommt der Text in jedes Feld; sonst je Zeile eines."))
        self.bogen = Auswahlfeld(); self.bogen.addItems(list(etiketten_boegen()))
        self.text = QPlainTextEdit("Vorname Nachname\nStraße 1\n12345 Ort"); self.text.setFixedHeight(HOEHE_TEXT_NORMAL)
        self.gleich = Auswahlfeld(); self.gleich.addItems(["ja — derselbe Text", "nein — je Zeile ein Etikett"])
        f.zeile("Bogen", self.bogen); f.zeile("Aufschrift", self.text); f.zeile("Überall dasselbe", self.gleich)
        f.breit(ok_zeile(self, "Anlegen"))
