"""Eigene zeichnung dialog: aus ``vcl.qt.widgets.dialoge.oberflaeche_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QLabel, QMessageBox, QPlainTextEdit, QWidget
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
from vcl.qt.widgets.bausteine.abstaende.mass import SCHRIFT_UEBERSCHRIFT_PLUS_PT
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_VORSCHAU_QUADRAT, HOEHE_BEREICH_MITTEL
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.oberflaeche_dialoge_hilfen import _satz


class EigeneZeichnungDialog(PanelFaehig, QDialog):
    """„Eigene Zeichnung …“: eine SVG-Datei oder nur Pfaddaten hineinkopieren; die Vorschau zeichnet beim Tippen mit."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Eigene Zeichnung")
        self.wert: str | None = None
        v = _spalte("standard", self)
        inhalt = QWidget(); g = FormularGitter(inhalt)
        t = QLabel("Eigene Zeichnung"); f = t.font(); f.setBold(True); f.setPointSizeF(f.pointSizeF() + SCHRIFT_UEBERSCHRIFT_PLUS_PT); t.setFont(f)
        g.breit(t)
        g.breit(_satz("Eine SVG-Datei hier hineinkopieren — oder nur die Pfaddaten. Sie wird auf 24 × 24 gebracht und mittig eingepasst."))
        self.feld = QPlainTextEdit(); self.feld.setPlaceholderText('<svg viewBox="0 0 24 24">…</svg>')
        self.feld.setMinimumHeight(HOEHE_BEREICH_MITTEL); self.feld.setAccessibleName("SVG oder Pfaddaten")
        g.breit(self.feld)
        self.bild = QLabel(); self.bild.setFixedSize(*GROESSE_VORSCHAU_QUADRAT); self.bild.setAlignment(Qt.AlignCenter)
        eigenschaft(self.bild, rolle="rahmen")
        self.wort = QLabel("Noch nichts"); self.wort.setWordWrap(True)
        vorschau = FlussLayout(10); vorschau.addWidget(self.bild); vorschau.addWidget(self.wort)
        g.breit(vorschau)
        self.gefuellt = UmbruchSchalter("Gefüllt zeichnen (für Zeichnungen aus Flächen statt Strichen)")
        g.breit(self.gefuellt)
        v.addWidget(inhalt)
        fussleiste(self, v, bei_ok=self._ok, ok_text="Übernehmen")
        self.feld.textChanged.connect(self._schau); self.gefuellt.toggled.connect(self._schau)
        self._schau()

    def _schau(self) -> None:
        self.wert = symbole.eigene_zeichnung(self.feld.toPlainText(), self.gefuellt.isChecked())
        if self.wert is None:
            self.bild.clear()
            self.wort.setText("Daraus wird keine Zeichnung." if self.feld.toPlainText().strip() else "Noch nichts")
            return
        farbe = self.palette().color(self.foregroundRole()).name()
        self.bild.setPixmap(QPixmap.fromImage(symbole.pfad_bild(self.wert, 80, farbe)))
        self.wort.setText("So kommt sie in die Leiste.")

    def _ok(self) -> None:
        if self.wert is None:
            QMessageBox.information(self, "Eigene Zeichnung", "Daraus wird keine Zeichnung — steht wirklich eine SVG darin?")
            return
        self.accept()
