"""Dialog „Beschriftungsnummerierung“: Schreibweise der Nummer. Kapitelnummern kennt Lunivo noch nicht (grau)."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QWidget

from framework.befehle.verweise.konstanten import NUMMERIERUNGSFORMATE
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.haken.haken import haken
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.verweise.dialog_hilfen import titel as _titel


class NummerierungDialog(PanelFaehig, QDialog):
    """„Beschriftungsnummerierung“: Schreibweise der Nummer. Kapitelnummern kennt Lunivo noch nicht (grau)."""

    def __init__(self, parent=None, zahl: str = "arabisch"):
        super().__init__(parent)
        self.setWindowTitle("Beschriftungsnummerierung")
        v = _spalte("standard", self)
        self.format = Auswahlfeld(); self.format.setAccessibleName("Format")
        for k, t in NUMMERIERUNGSFORMATE:
            self.format.addItem(t, k)
        self.format.setCurrentIndex(max(0, self.format.findData(zahl)))
        fw = QWidget(); fg = FormularGitter(fw)
        kapitel = haken("standard", "&Kapitelnummer einbeziehen", aktiv=False)
        fg.zeile(_titel("&Format:", self.format), self.format); fg.breit(kapitel); v.addWidget(fw)
        fussleiste(self, v)

    def zahl(self) -> str:
        return self.format.currentData()
