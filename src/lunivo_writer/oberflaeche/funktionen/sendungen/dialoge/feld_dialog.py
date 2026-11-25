"""Dialog „Seriendruckfeld einfügen“: die Spalten der Datenquelle; ohne Datenquelle ein Name zum Eintippen.

    d = FeldDialog(parent, spalten)      # d.einfuegen(name) bei jedem Klick, Fenster bleibt offen"""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog, QLabel, QListWidget

from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import knopfzeile
from lunivo_writer.oberflaeche.baukasten.basis.mass import HOEHE_LISTE_HOCH
from lunivo_writer.oberflaeche.baukasten.bausteine.feld.feld import zeilenfeld
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FormularGitter
from lunivo_writer.oberflaeche.baukasten.geruest.rollen import spalte as _spalte
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig


class FeldDialog(PanelFaehig, QDialog):
    """„Seriendruckfeld einfügen“: die Spalten der Datenquelle; ohne Datenquelle ein Name zum Eintippen. „Einfügen“ meldet
    ``einfuegen(name)`` und lässt das Fenster offen."""

    einfuegen = Signal(str)

    def __init__(self, parent=None, spalten: list[str] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Seriendruckfeld einfügen")
        v = _spalte("standard", self)
        self.liste = QListWidget(); self.liste.addItems(list(spalten or [])); self.liste.setMinimumHeight(HOEHE_LISTE_HOCH)
        self.liste.setAccessibleName("Felder")
        titel = QLabel("&Datenbankfelder:"); titel.setBuddy(self.liste)
        v.addWidget(titel); v.addWidget(self.liste, 1)
        self.name = zeilenfeld("standard", platzhalter="Name eines Feldes", name="Feldname")
        t2 = QLabel("&Feldname:"); t2.setBuddy(self.name)
        z = FormularGitter(); z.zeile(t2, self.name); v.addLayout(z)
        self.zeile = knopfzeile(self, ok_text="Einfügen", bei_ok=self._melden)
        v.addWidget(self.zeile)
        self.liste.currentTextChanged.connect(self.name.setText)
        self.liste.itemDoubleClicked.connect(lambda _it: self._melden())
        self.name.textChanged.connect(lambda t: self.zeile.ok.setEnabled(bool(t.strip())))
        if self.liste.count():
            self.liste.setCurrentRow(0)
        self.zeile.ok.setEnabled(bool(self.name.text().strip()))

    def _melden(self) -> None:
        n = " ".join(self.name.text().replace("{", "").replace("}", "").split())
        if n:
            self.einfuegen.emit(n)
            self.zeile.abbrechen.setText("Schließen")
