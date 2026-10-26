"""Das Fenster „Groß-/Kleinschreibung“ als Baustein: eine der fünf Arten wählen.

    d = SchreibweiseDialog(parent, "satz")
    if d.exec(): d.art()                                       # Schlüssel aus ``editor.schreibweise.SCHREIBWEISEN``

Das Fenster ändert keinen Text; der Aufrufer wendet die Art an (``Befehle.schreibweise``).
"""
from __future__ import annotations

from PySide6.QtWidgets import QButtonGroup, QDialog, QRadioButton, QVBoxLayout

from lunivo_writer.editor.schreibweise import SCHREIBWEISEN
from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.formular_gitter import abschnittstitel
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig


class SchreibweiseDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, art: str = "satz"):
        super().__init__(parent)
        self.setWindowTitle("Groß-/Kleinschreibung")
        v = QVBoxLayout(self)
        v.addWidget(abschnittstitel("Groß-/Kleinschreibung"))
        self._gruppe = QButtonGroup(self)
        for i, (k, text) in enumerate(SCHREIBWEISEN):
            r = QRadioButton(text); r.setChecked(k == art); self._gruppe.addButton(r, i); v.addWidget(r)
        v.addStretch(1)
        fussleiste(self, v)

    def art(self) -> str:
        return SCHREIBWEISEN[max(0, self._gruppe.checkedId())][0]
