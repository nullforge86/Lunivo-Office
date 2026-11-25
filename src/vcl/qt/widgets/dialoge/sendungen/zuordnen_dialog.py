"""Dialog „Übereinstimmende Felder festlegen“: zu jedem Feld im Text die Spalte der Datenquelle, aus der es seinen Wert bekommt.

    d = ZuordnenDialog(parent, felder, spalten, zuordnung)     # if d.exec(): d.ergebnis() → {Feld im Text: Spalte}"""
from __future__ import annotations

from PySide6.QtWidgets import QComboBox, QDialog, QLabel

from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig

OHNE = "(nicht zugeordnet)"


class ZuordnenDialog(PanelFaehig, QDialog):
    """„Übereinstimmende Felder festlegen“: zu jedem Feld im Text die Spalte der Datenquelle, aus der es seinen Wert bekommt."""

    def __init__(self, parent=None, felder: list[str] | None = None, spalten: list[str] | None = None, zuordnung: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Übereinstimmende Felder festlegen")
        zuordnung = dict(zuordnung or {})
        spalten = list(spalten or [])
        v = _spalte("standard", self)
        hinweis = QLabel("Hat ein Feld im Text einen anderen Namen als die Spalte der Empfängerliste, hier die Spalte wählen.")
        hinweis.setWordWrap(True); v.addWidget(hinweis)
        g = FormularGitter()                                                   # schmal: Spalte unter dem Feldnamen
        kopf = QLabel("Spalte der Empfängerliste"); kopf.setWordWrap(True)
        g.zeile(QLabel("Feld im Text"), kopf)
        self.wahl: dict[str, QComboBox] = {}
        for i, f in enumerate(felder or [], 1):
            cb = Auswahlfeld(); cb.addItem(OHNE, ""); cb.setAccessibleName(f)
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
