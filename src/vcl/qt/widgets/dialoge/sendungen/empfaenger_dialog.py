"""Dialog „Seriendruckempfänger“: alle Sätze der Datenquelle als Tabelle, je Zeile ein Haken; „Alle“ und „Keine“.

    d = EmpfaengerDialog(parent, spalten, saetze, aktiv)      # if d.exec(): d.ergebnis() → [bool je Satz]

Das Fenster ändert das Dokument nicht; der Aufrufer setzt das Ergebnis um."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractItemView, QDialog, QLabel, QTableWidget, QTableWidgetItem

from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_SERIENBRIEF
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig


class EmpfaengerDialog(PanelFaehig, QDialog):
    """„Seriendruckempfänger“: alle Sätze der Datenquelle als Tabelle, je Zeile ein Haken; „Alle“ und „Keine“."""

    def __init__(self, parent=None, spalten: list[str] | None = None, saetze: list[dict] | None = None, aktiv: list[bool] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Seriendruckempfänger")
        self.resize(*GROESSE_FENSTER_SERIENBRIEF)
        spalten, saetze = list(spalten or []), list(saetze or [])
        aktiv = list(aktiv) if aktiv is not None and len(aktiv) == len(saetze) else [True] * len(saetze)
        v = _spalte("standard", self)
        hinweis = QLabel("Diese Empfänger bekommen einen Brief. Haken entfernen, um einen Empfänger auszulassen."); hinweis.setWordWrap(True)
        v.addWidget(hinweis)
        self.tabelle = QTableWidget(len(saetze), len(spalten)); self.tabelle.setAccessibleName("Empfänger")
        self.tabelle.setHorizontalHeaderLabels(spalten)
        self.tabelle.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabelle.setSelectionBehavior(QAbstractItemView.SelectRows)
        for z, satz in enumerate(saetze):
            for s, name in enumerate(spalten):
                it = QTableWidgetItem(str(satz.get(name, "")))
                if s == 0:
                    it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
                    it.setCheckState(Qt.Checked if aktiv[z] else Qt.Unchecked)
                self.tabelle.setItem(z, s, it)
        self.tabelle.resizeColumnsToContents()
        v.addWidget(self.tabelle, 1)
        alle = knopf("gross", "&Alle", aktion=lambda: self._alle(True))
        keine = knopf("gross", "&Keine", aktion=lambda: self._alle(False))
        fussleiste(self, v, alle, keine)

    def _alle(self, an: bool) -> None:
        for z in range(self.tabelle.rowCount()):
            self.tabelle.item(z, 0).setCheckState(Qt.Checked if an else Qt.Unchecked)

    def ergebnis(self) -> list[bool]:
        return [self.tabelle.item(z, 0).checkState() == Qt.Checked for z in range(self.tabelle.rowCount())]
