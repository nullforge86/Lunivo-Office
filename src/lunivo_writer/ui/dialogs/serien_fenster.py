"""Fenster des Reiters „Mailings“ (Seriendruck): Empfänger auswählen, Seriendruckfeld einfügen, übereinstimmende Felder festlegen.

    d = EmpfaengerDialog(parent, spalten, saetze, aktiv)      # if d.exec(): d.ergebnis() → [bool je Satz]
    d = FeldDialog(parent, spalten)                            # d.einfuegen(name) bei jedem Klick, Fenster bleibt offen
    d = ZuordnenDialog(parent, felder, spalten, zuordnung)     # if d.exec(): d.ergebnis() → {Feld im Text: Spalte}

Die Fenster ändern das Dokument nicht; der Aufrufer (``Befehle``) setzt das Ergebnis um.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout,
)

from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig
from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste, knopfzeile

OHNE = "(nicht zugeordnet)"


class EmpfaengerDialog(PanelFaehig, QDialog):
    """„Seriendruckempfänger“: alle Sätze der Datenquelle als Tabelle, je Zeile ein Haken; „Alle“ und „Keine“."""

    def __init__(self, parent=None, spalten: list[str] | None = None, saetze: list[dict] | None = None, aktiv: list[bool] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Seriendruckempfänger")
        self.resize(720, 440)
        spalten, saetze = list(spalten or []), list(saetze or [])
        aktiv = list(aktiv) if aktiv is not None and len(aktiv) == len(saetze) else [True] * len(saetze)
        v = QVBoxLayout(self)
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
        alle, keine = QPushButton("&Alle"), QPushButton("&Keine")
        for k, an in ((alle, True), (keine, False)):
            k.setMinimumHeight(36); k.clicked.connect(lambda _=False, a=an: self._alle(a))
        fussleiste(self, v, alle, keine)

    def _alle(self, an: bool) -> None:
        for z in range(self.tabelle.rowCount()):
            self.tabelle.item(z, 0).setCheckState(Qt.Checked if an else Qt.Unchecked)

    def ergebnis(self) -> list[bool]:
        return [self.tabelle.item(z, 0).checkState() == Qt.Checked for z in range(self.tabelle.rowCount())]


class FeldDialog(PanelFaehig, QDialog):
    """„Seriendruckfeld einfügen“: die Spalten der Datenquelle; ohne Datenquelle ein Name zum Eintippen. „Einfügen“ meldet
    ``einfuegen(name)`` und lässt das Fenster offen."""

    einfuegen = Signal(str)

    def __init__(self, parent=None, spalten: list[str] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Seriendruckfeld einfügen")
        v = QVBoxLayout(self)
        self.liste = QListWidget(); self.liste.addItems(list(spalten or [])); self.liste.setMinimumHeight(200)
        self.liste.setAccessibleName("Felder")
        titel = QLabel("&Datenbankfelder:"); titel.setBuddy(self.liste)
        v.addWidget(titel); v.addWidget(self.liste, 1)
        self.name = QLineEdit(); self.name.setMinimumHeight(34); self.name.setAccessibleName("Feldname")
        self.name.setPlaceholderText("Name eines Feldes")
        t2 = QLabel("&Feldname:"); t2.setBuddy(self.name)
        z = QHBoxLayout(); z.addWidget(t2); z.addWidget(self.name, 1); v.addLayout(z)
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


class ZuordnenDialog(PanelFaehig, QDialog):
    """„Übereinstimmende Felder festlegen“: zu jedem Feld im Text die Spalte der Datenquelle, aus der es seinen Wert bekommt."""

    def __init__(self, parent=None, felder: list[str] | None = None, spalten: list[str] | None = None, zuordnung: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Übereinstimmende Felder festlegen")
        zuordnung = dict(zuordnung or {})
        spalten = list(spalten or [])
        v = QVBoxLayout(self)
        from lunivo_writer.ui.baukasten.formular_gitter import FormularGitter
        hinweis = QLabel("Hat ein Feld im Text einen anderen Namen als die Spalte der Empfängerliste, hier die Spalte wählen.")
        hinweis.setWordWrap(True); v.addWidget(hinweis)
        g = FormularGitter()                                                   # schmal: Spalte unter dem Feldnamen
        kopf = QLabel("Spalte der Empfängerliste"); kopf.setWordWrap(True)
        g.zeile(QLabel("Feld im Text"), kopf)
        self.wahl: dict[str, QComboBox] = {}
        for i, f in enumerate(felder or [], 1):
            cb = QComboBox(); cb.addItem(OHNE, ""); cb.setMinimumHeight(34); cb.setAccessibleName(f)
            for s in spalten:
                cb.addItem(s, s)
            soll = zuordnung.get(f, f if f in spalten else "")
            cb.setCurrentIndex(max(0, cb.findData(soll)))
            titel = QLabel(f); titel.setBuddy(cb)
            g.zeile(titel, cb)
            self.wahl[f] = cb
        v.addLayout(g)
        v.addStretch(1)
        fussleiste(self, v)

    def ergebnis(self) -> dict:
        return {f: cb.currentData() for f, cb in self.wahl.items() if cb.currentData()}
