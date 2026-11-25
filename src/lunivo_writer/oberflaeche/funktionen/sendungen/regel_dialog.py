"""Dialog „Regel“: Wenn das Feld den Wert hat, steht der erste Text da, sonst der zweite."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLineEdit

from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FormularGitter
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.funktionen.sendungen.dialog_hilfen import hinweis, ok_zeile


class RegelDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Regel")
        f = FormularGitter(self)
        f.breit(hinweis("Wenn das Feld den Wert hat, steht der erste Text da — sonst der zweite."))
        self.feld = QLineEdit("Geschlecht"); self.wert = QLineEdit("w")
        self.dann = QLineEdit("Sehr geehrte Frau"); self.sonst = QLineEdit("Sehr geehrter Herr")
        for lab, w in (("Feld", self.feld), ("ist gleich", self.wert), ("dann", self.dann), ("sonst", self.sonst)):
            f.zeile(lab, w)
        f.breit(ok_zeile(self, "Einfügen"))
