"""Table dialog: aus ``vcl.qt.widgets.dialoge.dokument_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.option.option import option
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog, QLabel, QSpinBox, QWidget
from vcl.qt.widgets.bausteine.interaktion.felder.mass_feld import spin as _spin
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile


def _titel(text: str, feld) -> QLabel:
    t = QLabel(text); t.setBuddy(feld)
    return t


class TableDialog(PanelFaehig, QDialog):
    """„Tabelle einfügen“ wie in der Vorlage: Tabellengröße, Einstellung für optimale Breite, Abmessungen für neue Tabellen speichern.
    ``vorgabe``: (Spalten, Zeilen) aus den Einstellungen; ``speichern.isChecked()`` sagt dem Aufrufer, ob er sie merken soll."""

    def __init__(self, parent=None, vorgabe: tuple[int, int] = (5, 2)):
        from PySide6.QtWidgets import QButtonGroup, QRadioButton
        super().__init__(parent)
        self.setWindowTitle("Tabelle einfügen")
        lay = _spalte("standard", self)
        lay.addWidget(QLabel("Tabellengröße"))
        self.cols = QSpinBox(); self.cols.setRange(1, 63); self.cols.setValue(vorgabe[0])
        self.rows = QSpinBox(); self.rows.setRange(1, 500); self.rows.setValue(vorgabe[1])
        gi = QWidget(); g = FormularGitter(gi)
        for feld in (self.cols, self.rows):
            pass
        g.reihe((_titel("Spaltenan&zahl:", self.cols), self.cols), (_titel("Zeilenan&zahl:", self.rows), self.rows))
        lay.addWidget(gi)
        lay.addWidget(QLabel("Einstellung für optimale Breite"))
        self.fest = option("standard", "Feste Spalten&breite:")
        self.auto = option("standard", "Spaltenbreite automatisch anpassen (&S)", an=True)
        gruppe = QButtonGroup(self); gruppe.addButton(self.fest); gruppe.addButton(self.auto)
        self.breite = _spin(30.0, 2.0, 500.0)
        self.breite.setAccessibleName("Feste Spaltenbreite")
        zi = QWidget(); z = FormularGitter(zi)
        z.reihe(("", self.fest), ("", self.breite)); z.breit(self.auto)
        lay.addWidget(zi)
        self.fest.toggled.connect(self.breite.setEnabled); self.breite.setEnabled(False)
        self.speichern = UmbruchSchalter("Ab&messungen für neue Tabellen speichern")
        lay.addWidget(self.speichern)
        lay.addStretch(1)
        lay.addWidget(knopfzeile(self))

    def spaltenbreite_px(self) -> float | None:
        """Feste Breite jeder Spalte in Bildpunkten; None: automatisch (Seitenbreite)."""
        return self.breite.value() * 96 / 25.4 if self.fest.isChecked() else None
