"""Das Fenster „Phonetisches Leitzeichen“ als Baustein: der Text in Teilen (je eine Zeile), zu jedem Teil sein Leittext, dazu Ausrichtung, Abstand, Schrift und Größe.

    d = RubyDialog(parent, [("H", ""), ("a", ""), ("l", "")])         # [(Basistext, Leittext)]
    if d.exec(): d.zeilen()                                         # [(Basistext, Leittext, {"ausrichtung", "abstand", "groesse", "schrift"})]

„Gruppieren“ fasst die gewählten Zeilen zu einer zusammen, „Mono“ teilt eine in einzelne Zeichen, „Alle entfernen“ löscht die Leittexte,
„Standardanzeige“ stellt Ausrichtung, Abstand und Größe der gewählten Zeile zurück, „Alles ändern“ überträgt sie auf alle Zeilen.
Das Fenster ändert keinen Text; der Aufrufer setzt ``P_RUBY`` (``Befehle.phonetischesLeitzeichen``).
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QDialog, QFontComboBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from lunivo_writer.editor.zeichenzusatz import AUSRICHTUNGEN
from lunivo_writer.ui.baukasten.dialog_rahmen import VorschauFlaeche, fussleiste
from lunivo_writer.ui.baukasten.formular_gitter import FlussLayout, FormularGitter
from lunivo_writer.ui.baukasten.mass_feld import spin
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

STANDARD = {"ausrichtung": "zentriert", "abstand": 0.0, "groesse": 7.0}


class RubyDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, teile=(), schrift: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Phonetisches Leitzeichen")
        self._wie: list[dict] = []
        self._schrift = schrift
        v = QVBoxLayout(self)
        self.tabelle = QTableWidget(0, 2); self.tabelle.setHorizontalHeaderLabels(["Basistext:", "Ruby-Text:"])
        self.tabelle.verticalHeader().setVisible(False); self.tabelle.horizontalHeader().setStretchLastSection(True)
        self.tabelle.setSelectionBehavior(QAbstractItemView.SelectRows); self.tabelle.setMinimumHeight(110)
        for basis, ruby in teile:
            self._zeile_anhaengen(basis, ruby)
        v.addWidget(self.tabelle)
        tasten = FlussLayout(6); tasten.setContentsMargins(0, 0, 0, 0)
        self.gruppieren, self.mono = QPushButton("Gruppieren"), QPushButton("Mono")
        self.alle_weg, self.standard, self.ton = QPushButton("Alle entfernen"), QPushButton("Standardanzeige"), QPushButton("Ton")
        self.ton.setEnabled(False); self.ton.setToolTip("Nur für asiatische Schriften")
        for b in (self.gruppieren, self.mono, self.alle_weg, self.standard, self.ton):
            tasten.addWidget(b)
        v.addLayout(tasten)
        g = FormularGitter(); g.setContentsMargins(0, 0, 0, 0)
        self.ausrichtung = QComboBox()
        for k, t in AUSRICHTUNGEN:
            self.ausrichtung.addItem(t, k)
        self.abstand = spin(0.0, -20.0, 40.0, " pt", 0.5, 1)
        self.schrift = QFontComboBox(); self.schrift.setEditable(False)
        if schrift:
            self.schrift.setCurrentFont(QFont(schrift))
        self.groesse = spin(7.0, 2.0, 60.0, " pt", 0.5, 1)
        g.reihe(("Ausrichtung:", self.ausrichtung), ("Offset:", self.abstand))
        g.reihe(("Schriftart:", self.schrift), ("Größe:", self.groesse))
        v.addLayout(g)
        self.vorschau = VorschauFlaeche(self._malen, 54); v.addWidget(self.vorschau)
        self.alles = QPushButton("Alles ändern …")
        fussleiste(self, v, self.alles)
        self.gruppieren.clicked.connect(self._gruppieren); self.mono.clicked.connect(self._mono)
        self.alle_weg.clicked.connect(self._alle_weg); self.standard.clicked.connect(self._standard)
        self.alles.clicked.connect(self._alles)
        self.tabelle.currentCellChanged.connect(self._zeile_gewaehlt)
        self.tabelle.itemChanged.connect(lambda *_: self.vorschau.update())
        for w in (self.ausrichtung.currentIndexChanged, self.abstand.valueChanged, self.groesse.valueChanged):
            w.connect(self._feld_geaendert)
        if self.tabelle.rowCount():
            self.tabelle.setCurrentCell(0, 1)
        self.resize(430, 420)

    # ---- Zeilen ----
    def _zeile_anhaengen(self, basis: str, ruby: str, wie: dict | None = None, an: int | None = None) -> None:
        z = self.tabelle.rowCount() if an is None else an
        self.tabelle.insertRow(z)
        b = QTableWidgetItem(basis); b.setFlags(b.flags() & ~Qt.ItemIsEditable)
        self.tabelle.setItem(z, 0, b); self.tabelle.setItem(z, 1, QTableWidgetItem(ruby))
        self._wie.insert(z, dict(wie or STANDARD))

    def _gewaehlt(self) -> list[int]:
        return sorted({i.row() for i in self.tabelle.selectedIndexes()})

    def _gruppieren(self) -> None:
        zeilen = self._gewaehlt()
        if len(zeilen) < 2:
            return
        basis = "".join(self.tabelle.item(r, 0).text() for r in zeilen)
        ruby = " ".join(t for t in (self.tabelle.item(r, 1).text() for r in zeilen) if t)
        wie = dict(self._wie[zeilen[0]])
        for r in reversed(zeilen):
            self.tabelle.removeRow(r); del self._wie[r]
        self._zeile_anhaengen(basis, ruby, wie, zeilen[0]); self.tabelle.selectRow(zeilen[0]); self.vorschau.update()

    def _mono(self) -> None:
        for r in reversed(self._gewaehlt()):
            basis, wie = self.tabelle.item(r, 0).text(), dict(self._wie[r])
            ruby = self.tabelle.item(r, 1).text().split()
            if len(basis) < 2:
                continue
            self.tabelle.removeRow(r); del self._wie[r]
            for i, ch in enumerate(basis):
                self._zeile_anhaengen(ch, ruby[i] if len(ruby) == len(basis) else "", wie, r + i)
        self.vorschau.update()

    def _alle_weg(self) -> None:
        for r in range(self.tabelle.rowCount()):
            self.tabelle.item(r, 1).setText("")

    def _standard(self) -> None:
        r = self.tabelle.currentRow()
        if r >= 0:
            self._wie[r] = dict(STANDARD); self._zeile_gewaehlt(r, 0, 0, 0)

    def _alles(self) -> None:
        r = self.tabelle.currentRow()
        if r >= 0:
            for i in range(len(self._wie)):
                self._wie[i] = dict(self._wie[r])
            self.vorschau.update()

    def _zeile_gewaehlt(self, r: int, _c: int, _vr: int, _vc: int) -> None:
        if r < 0 or r >= len(self._wie):
            return
        w = self._wie[r]
        for feld in (self.ausrichtung, self.abstand, self.groesse):
            feld.blockSignals(True)
        self.ausrichtung.setCurrentIndex(max(0, self.ausrichtung.findData(w["ausrichtung"])))
        self.abstand.setValue(w["abstand"]); self.groesse.setValue(w["groesse"])
        for feld in (self.ausrichtung, self.abstand, self.groesse):
            feld.blockSignals(False)
        self.alles.setEnabled(len(self._wie) > 1)
        self.vorschau.update()

    def _feld_geaendert(self, *_) -> None:
        r = self.tabelle.currentRow()
        if 0 <= r < len(self._wie):
            self._wie[r] = {"ausrichtung": self.ausrichtung.currentData(), "abstand": self.abstand.value(), "groesse": self.groesse.value()}
        self.vorschau.update()

    def _malen(self, p, rect) -> None:
        f = QFont(self.schrift.currentFont()); f.setPixelSize(22); p.setFont(f)
        x = rect.left() + 10
        for r in range(self.tabelle.rowCount()):
            basis, ruby, w = self.tabelle.item(r, 0).text(), self.tabelle.item(r, 1).text(), self._wie[r]
            p.setFont(f); breite = p.fontMetrics().horizontalAdvance(basis)
            p.setPen(Qt.black); p.drawText(int(x), int(rect.bottom() - 6), basis)
            if ruby:
                k = QFont(f); k.setPixelSize(max(6, int(w["groesse"] * 1.6))); p.setFont(k)
                rb = p.fontMetrics().horizontalAdvance(ruby)
                dx = {"links": 0, "rechts": breite - rb}.get(w["ausrichtung"], (breite - rb) / 2)
                p.drawText(int(x + dx), int(rect.bottom() - 30 - w["abstand"]), ruby)
            x += max(breite, 4)

    def zeilen(self) -> list[tuple[str, str, dict]]:
        return [(self.tabelle.item(r, 0).text(), self.tabelle.item(r, 1).text().strip(), {**self._wie[r], "schrift": self.schrift.currentFont().family()})
                for r in range(self.tabelle.rowCount())]
