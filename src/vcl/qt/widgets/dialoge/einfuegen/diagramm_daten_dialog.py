"""Diagramm daten dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QWidget
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_TABELLE, HOEHE_LISTE_MITTEL
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig


class DiagrammDatenDialog(PanelFaehig, QDialog):
    """Titel und Daten des Diagramms (Unterfenster von „Diagramm einfügen“): erste Spalte Rubriken, weitere Spalten Datenreihen."""

    def __init__(self, parent, titel: str, kategorien: list[str], reihen: dict[str, list[float]]):
        super().__init__(parent)
        from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
        from PySide6.QtWidgets import QWidget
        from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
        from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
        self.setWindowTitle("Daten bearbeiten")
        v = _spalte("standard", self)
        kopf = QWidget(); g = FormularGitter(kopf)
        self.titel = zeilenfeld("frei", titel); g.zeile("&Titel:", self.titel)
        v.addWidget(kopf)
        self.tab = QTableWidget(len(kategorien), len(reihen) + 1)
        self.tab.setHorizontalHeaderLabels(["Rubrik"] + list(reihen))
        self.tab.setMinimumHeight(HOEHE_LISTE_MITTEL)
        for r, k in enumerate(kategorien):
            self.tab.setItem(r, 0, QTableWidgetItem(k))
            for c, werte in enumerate(reihen.values(), 1):
                self.tab.setItem(r, c, QTableWidgetItem(f"{werte[r]:g}" if r < len(werte) else "0"))
        v.addWidget(self.tab)
        z = FlussLayout(6)
        for text, fn in (("Zeile hinzufügen", lambda: self.tab.setRowCount(self.tab.rowCount() + 1)),
                         ("Zeile entfernen", lambda: self.tab.setRowCount(max(1, self.tab.rowCount() - 1))),
                         ("Reihe hinzufügen", self._reihe_dazu),
                         ("Reihe entfernen", lambda: self.tab.setColumnCount(max(2, self.tab.columnCount() - 1)))):
            z.addWidget(knopf("standard", text, aktion=fn))
        v.addLayout(z)
        fussleiste(self, v)
        self.resize(*GROESSE_FENSTER_TABELLE)

    def _reihe_dazu(self) -> None:
        n = self.tab.columnCount()
        self.tab.setColumnCount(n + 1); self.tab.setHorizontalHeaderItem(n, QTableWidgetItem(f"Datenreihe {n}"))

    def daten(self) -> tuple[str, list[str], dict[str, list[float]]]:
        kat, reihen = [], {}
        for c in range(1, self.tab.columnCount()):
            kopf = self.tab.horizontalHeaderItem(c)
            reihen[kopf.text() if kopf else f"Datenreihe {c}"] = []
        for r in range(self.tab.rowCount()):
            k = self.tab.item(r, 0)
            kat.append(k.text() if k else "")
            for c, name in enumerate(reihen, 1):
                it = self.tab.item(r, c)
                try:
                    reihen[name].append(float((it.text() if it else "0").replace(",", ".")))
                except ValueError:
                    reihen[name].append(0.0)
        return self.titel.text(), kat, reihen


class DiagrammDatenDialog(PanelFaehig, QDialog):
    """Titel und Daten des Diagramms (Unterfenster von „Diagramm einfügen“): erste Spalte Rubriken, weitere Spalten Datenreihen."""

    def __init__(self, parent, titel: str, kategorien: list[str], reihen: dict[str, list[float]]):
        super().__init__(parent)
        from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
        from PySide6.QtWidgets import QWidget
        from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
        from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
        self.setWindowTitle("Daten bearbeiten")
        v = _spalte("standard", self)
        kopf = QWidget(); g = FormularGitter(kopf)
        self.titel = zeilenfeld("frei", titel); g.zeile("&Titel:", self.titel)
        v.addWidget(kopf)
        self.tab = QTableWidget(len(kategorien), len(reihen) + 1)
        self.tab.setHorizontalHeaderLabels(["Rubrik"] + list(reihen))
        self.tab.setMinimumHeight(HOEHE_LISTE_MITTEL)
        for r, k in enumerate(kategorien):
            self.tab.setItem(r, 0, QTableWidgetItem(k))
            for c, werte in enumerate(reihen.values(), 1):
                self.tab.setItem(r, c, QTableWidgetItem(f"{werte[r]:g}" if r < len(werte) else "0"))
        v.addWidget(self.tab)
        z = FlussLayout(6)
        for text, fn in (("Zeile hinzufügen", lambda: self.tab.setRowCount(self.tab.rowCount() + 1)),
                         ("Zeile entfernen", lambda: self.tab.setRowCount(max(1, self.tab.rowCount() - 1))),
                         ("Reihe hinzufügen", self._reihe_dazu),
                         ("Reihe entfernen", lambda: self.tab.setColumnCount(max(2, self.tab.columnCount() - 1)))):
            z.addWidget(knopf("standard", text, aktion=fn))
        v.addLayout(z)
        fussleiste(self, v)
        self.resize(*GROESSE_FENSTER_TABELLE)

    def _reihe_dazu(self) -> None:
        n = self.tab.columnCount()
        self.tab.setColumnCount(n + 1); self.tab.setHorizontalHeaderItem(n, QTableWidgetItem(f"Datenreihe {n}"))

    def daten(self) -> tuple[str, list[str], dict[str, list[float]]]:
        kat, reihen = [], {}
        for c in range(1, self.tab.columnCount()):
            kopf = self.tab.horizontalHeaderItem(c)
            reihen[kopf.text() if kopf else f"Datenreihe {c}"] = []
        for r in range(self.tab.rowCount()):
            k = self.tab.item(r, 0)
            kat.append(k.text() if k else "")
            for c, name in enumerate(reihen, 1):
                it = self.tab.item(r, c)
                try:
                    reihen[name].append(float((it.text() if it else "0").replace(",", ".")))
                except ValueError:
                    reihen[name].append(0.0)
        return self.titel.text(), kat, reihen
