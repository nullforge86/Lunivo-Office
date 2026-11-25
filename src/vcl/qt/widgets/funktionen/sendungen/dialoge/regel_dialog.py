"""Dialog „Regel“: Wenn das Feld den Wert hat, steht der erste Text da, sonst der zweite."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog

from vcl.qt.widgets.bausteine.bausteine.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.funktionen.sendungen.dialoge.dialog_hilfen import hinweis, ok_zeile


class RegelDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Regel")
        f = FormularGitter(self)
        f.breit(hinweis("Wenn das Feld den Wert hat, steht der erste Text da — sonst der zweite."))
        self.feld = zeilenfeld("frei", "Geschlecht"); self.wert = zeilenfeld("frei", "w")
        self.dann = zeilenfeld("frei", "Sehr geehrte Frau"); self.sonst = zeilenfeld("frei", "Sehr geehrter Herr")
        for lab, w in (("Feld", self.feld), ("ist gleich", self.wert), ("dann", self.dann), ("sonst", self.sonst)):
            f.zeile(lab, w)
        f.breit(ok_zeile(self, "Einfügen"))
