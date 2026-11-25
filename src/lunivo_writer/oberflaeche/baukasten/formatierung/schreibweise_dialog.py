"""Das Fenster „Groß-/Kleinschreibung“ als Baustein: eine der fünf Arten wählen.

    d = SchreibweiseDialog(parent, "satz")
    if d.exec(): d.art()                                       # Schlüssel aus ``editor.text.schreibweise.SCHREIBWEISEN``

Das Fenster ändert keinen Text; der Aufrufer wendet die Art an (``Befehle.schreibweise``).
"""
from __future__ import annotations

from lunivo_writer.oberflaeche.baukasten.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtWidgets import QButtonGroup, QDialog, QRadioButton

from lunivo_writer.editor.text.schreibweise import SCHREIBWEISEN
from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import fussleiste
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import abschnittstitel
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_KLEIN, RAND_PANEL_KLEIN


class SchreibweiseDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, art: str = "satz"):
        super().__init__(parent)
        self.setWindowTitle("Groß-/Kleinschreibung")
        v = _spalte("panel", self)
        v.addWidget(abschnittstitel("Groß-/Kleinschreibung"))
        self._gruppe = QButtonGroup(self)
        for i, (k, text) in enumerate(SCHREIBWEISEN):
            r = QRadioButton(text); r.setChecked(k == art); self._gruppe.addButton(r, i); v.addWidget(r)
        v.addStretch(1)
        fussleiste(self, v)

    def art(self) -> str:
        return SCHREIBWEISEN[max(0, self._gruppe.checkedId())][0]
