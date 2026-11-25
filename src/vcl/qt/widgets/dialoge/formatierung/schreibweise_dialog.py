"""Das Fenster „Groß-/Kleinschreibung“ als Baustein: eine der fünf Arten wählen.

    d = SchreibweiseDialog(parent, "satz")
    if d.exec(): d.art()                                       # Schlüssel aus ``editor.text.schreibweise.SCHREIBWEISEN``

Das Fenster ändert keinen Text; der Aufrufer wendet die Art an (``Befehle.schreibweise``).
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.option.option import option

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtWidgets import QButtonGroup, QDialog, QRadioButton

from vcl.qt.schrift.schreibweise import SCHREIBWEISEN
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import abschnittstitel
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_KLEIN, RAND_PANEL_KLEIN


class SchreibweiseDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, art: str = "satz"):
        super().__init__(parent)
        self.setWindowTitle("Groß-/Kleinschreibung")
        v = _spalte("panel", self)
        v.addWidget(abschnittstitel("Groß-/Kleinschreibung"))
        self._gruppe = QButtonGroup(self)
        for i, (k, text) in enumerate(SCHREIBWEISEN):
            r = option("standard", text, an=k == art, gruppe=self._gruppe, nummer=i); v.addWidget(r)
        v.addStretch(1)
        fussleiste(self, v)

    def art(self) -> str:
        return SCHREIBWEISEN[max(0, self._gruppe.checkedId())][0]
