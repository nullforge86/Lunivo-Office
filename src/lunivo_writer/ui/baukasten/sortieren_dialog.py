"""Das Fenster „Sortieren“ als Baustein: Reihenfolge und Art wählen; „Optionen …“ öffnet die Sortieroptionen als Unterfenster.

    d = SortierenDialog(parent)
    if d.exec(): d.werte()           # {"absteigend": bool, "typ": "text"|"zahl"|"datum", "gross_klein": bool}

Das Fenster sortiert nicht selbst; der Aufrufer ruft ``editor.schreibweise.sortiert`` auf (``Befehle.sortieren``).
"""
from __future__ import annotations

from PySide6.QtWidgets import QButtonGroup, QCheckBox, QComboBox, QDialog, QPushButton, QRadioButton, QVBoxLayout

from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.fenster_stapel import zeige_unter
from lunivo_writer.ui.baukasten.formular_gitter import FormularGitter, abschnittstitel
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig


class SortierOptionenDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, gross_klein: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Sortieroptionen")
        v = QVBoxLayout(self)
        v.addWidget(abschnittstitel("Sortieroptionen"))
        self.gross_klein = QCheckBox("Groß-/Kleinschreibung beachten"); self.gross_klein.setChecked(gross_klein)
        v.addWidget(self.gross_klein); v.addStretch(1)
        fussleiste(self, v)


class SortierenDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sortieren")
        self._gross_klein = False
        v = QVBoxLayout(self)
        g = FormularGitter(); g.setContentsMargins(0, 0, 0, 0)
        self.typ = QComboBox()
        for k, t in (("text", "Text"), ("zahl", "Zahl"), ("datum", "Datum")):
            self.typ.addItem(t, k)
        g.zeile("Art:", self.typ)
        v.addLayout(g)
        v.addWidget(abschnittstitel("Reihenfolge"))
        self._ordnung = QButtonGroup(self)
        for i, t in enumerate(("Aufsteigend", "Absteigend")):
            r = QRadioButton(t); r.setChecked(i == 0); self._ordnung.addButton(r, i); v.addWidget(r)
        v.addStretch(1)
        optionen = QPushButton("Optionen …"); optionen.clicked.connect(self._optionen)
        fussleiste(self, v, optionen)

    def _optionen(self) -> None:
        d = SortierOptionenDialog(self, self._gross_klein)
        zeige_unter(self, d, lambda: setattr(self, "_gross_klein", d.gross_klein.isChecked()))

    def werte(self) -> dict:
        return {"absteigend": self._ordnung.checkedId() == 1, "typ": self.typ.currentData(), "gross_klein": self._gross_klein}
