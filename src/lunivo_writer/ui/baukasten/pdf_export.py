"""„PDF-Datei exportieren“: das Fenster nach Kays Vorbild (WPS-Bildschirmfotos) mit den Reitern **Allgemein** und
**Berechtigungseinstellungen**.

Allgemein: Speichern unter (mit „Durchsuchen …“), Seitenbereich (Alles, Aktuelle Seite, Markierung, Seite(n) von–an) und die
Exportoptionen. Berechtigungseinstellungen: Verschlüsseln, Kennwort für die Rechte, was erlaubt bleibt, Druckberechtigung und
Kennwort zum Öffnen. Unten „Nach Abschluss des Exports schließen“, Abbrechen und OK.

Das Fenster schreibt nichts selbst: ``exportieren(PdfWahl) -> bool`` vom Aufrufer schreibt die Datei (``services/pdf_export.py``).
Bleibt das Fenster nach dem Export offen, steht darunter, was geschrieben wurde.
"""
from __future__ import annotations

import os
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QRadioButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget)

from lunivo_writer.services.pdf_export import DRUCK, PdfWahl, kennwort_fehler
from lunivo_writer.ui.baukasten.dialog_rahmen import knopfzeile

FELD_H = 32
OPTIONEN = [("eigenschaften", "&Zusammenfassungsinformationen"), ("textmarken", "Text&marke"),
            ("kommentare", "Neuer &Kommentar"), ("ueberschriften", "Überschriftformatvorlagen in &Textmarken"),
            ("hyperlinks", "&Hyperlink"), ("andere", "&Andere Formatvorlagen in Textmarken"),
            ("notenlinks", "Verknüpfung von Fuß&noten und Endnoten"), ("eigene", "&Benutzerdefinierte Formatvorlagen in Textmarken")]
RECHTE = [("aendern", "Ä&ndern zulassen"), ("kopieren", "Berechtigt zum &Kopieren"),
          ("kommentieren", "Berechtigt zum &Hinzufügen von Kommentaren")]


def _gruppe(titel: str, layout, buddy: QWidget | None = None) -> QWidget:
    """Überschrift über einem umrandeten Feld, wie im Vorbild."""
    w = QWidget()
    v = QVBoxLayout(w); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(4)
    kopf = QLabel(titel)
    if buddy:
        kopf.setBuddy(buddy)
    v.addWidget(kopf)
    rahmen = QFrame(); rahmen.setFrameShape(QFrame.StyledPanel)
    rahmen.setLayout(layout)
    v.addWidget(rahmen)
    return w


def _kennwort() -> QLineEdit:
    f = QLineEdit(); f.setEchoMode(QLineEdit.Password); f.setMinimumHeight(FELD_H)
    return f


class PdfExportFenster(QDialog):
    def __init__(self, parent, start: PdfWahl, seiten: int, aktuelle: int, markierung: bool,
                 exportieren: Callable[[PdfWahl], bool]):
        super().__init__(parent)
        self.setWindowTitle("PDF-Datei exportieren")
        self.setModal(True)
        self._exportieren = exportieren
        self._wahl: PdfWahl | None = None
        self._ersetzen_ok = ""                                       # dieser Pfad darf ohne Rückfrage ersetzt werden
        v = QVBoxLayout(self); v.setContentsMargins(12, 12, 12, 12); v.setSpacing(10)
        self.reiter = QTabWidget()
        self.reiter.addTab(self._allgemein(start, seiten, aktuelle, markierung), "Allgemein")
        self.reiter.addTab(self._rechte(start), "Berechtigungseinstellungen")
        v.addWidget(self.reiter, 1)
        self.meldung = QLabel(); self.meldung.setWordWrap(True); self.meldung.hide()
        v.addWidget(self.meldung)
        fuss = QHBoxLayout()
        self.schliessen = QCheckBox("Nach Abschluss des &Exports schließen"); self.schliessen.setChecked(start.schliessen)
        fuss.addWidget(self.schliessen)
        zeile = knopfzeile(self, bei_ok=self._ok)
        self.ok = zeile.ok
        fuss.addWidget(zeile, 1)
        v.addLayout(fuss)
        self.resize(660, 600)

    # ---- Allgemein ---------------------------------------------------------------------------------------------------
    def _allgemein(self, s: PdfWahl, seiten: int, aktuelle: int, markierung: bool) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(10, 10, 10, 10); v.setSpacing(10)

        h = QHBoxLayout(); h.setContentsMargins(8, 8, 8, 8)
        self.pfad = QLineEdit(s.pfad); self.pfad.setMinimumHeight(FELD_H)
        durch = QPushButton("&Durchsuchen …"); durch.setMinimumHeight(FELD_H); durch.clicked.connect(self._durchsuchen)
        h.addWidget(self.pfad, 1); h.addWidget(durch)
        v.addWidget(_gruppe("Speichern &unter", h, self.pfad))

        g = QGridLayout(); g.setContentsMargins(14, 10, 14, 10); g.setVerticalSpacing(10); g.setHorizontalSpacing(12)
        self.b_alles = QRadioButton("&Alles"); self.b_aktuell = QRadioButton(f"Aktuelle &Seite ({aktuelle})")
        self.b_markierung = QRadioButton("&Markierung"); self.b_seiten = QRadioButton("Seite(&n)")
        self.b_markierung.setEnabled(markierung)                         # nicht Mögliches bleibt grau sichtbar
        self._bereiche = {"alles": self.b_alles, "aktuell": self.b_aktuell, "markierung": self.b_markierung, "seiten": self.b_seiten}
        gruppe = QButtonGroup(w)
        for b in self._bereiche.values():
            gruppe.addButton(b)
        bereich = s.bereich if s.bereich != "markierung" or markierung else "alles"
        self._bereiche.get(bereich, self.b_alles).setChecked(True)
        self.von, self.bis = QSpinBox(), QSpinBox()
        for sp, wert in ((self.von, s.von), (self.bis, s.bis)):
            sp.setRange(1, max(1, seiten)); sp.setValue(min(max(1, wert), max(1, seiten))); sp.setMinimumHeight(FELD_H); sp.setMinimumWidth(110)
        if s.bereich != "seiten":
            self.von.setValue(1); self.bis.setValue(max(1, seiten))
        g.addWidget(self.b_alles, 0, 0); g.addWidget(self.b_aktuell, 1, 0); g.addWidget(self.b_markierung, 2, 0); g.addWidget(self.b_seiten, 3, 0)
        self.l_von, self.l_bis = QLabel("&Von:"), QLabel("A&n:")
        self.l_von.setBuddy(self.von); self.l_bis.setBuddy(self.bis)
        g.addWidget(self.l_von, 3, 1, Qt.AlignRight); g.addWidget(self.von, 3, 2); g.addWidget(self.l_bis, 3, 3, Qt.AlignRight); g.addWidget(self.bis, 3, 4)
        g.setColumnStretch(0, 1); g.setColumnStretch(5, 1)
        self.b_seiten.toggled.connect(self._seiten_schalten); self._seiten_schalten(self.b_seiten.isChecked())
        v.addWidget(_gruppe("Seitenbereich", g))

        g = QGridLayout(); g.setContentsMargins(14, 10, 14, 10); g.setVerticalSpacing(8); g.setHorizontalSpacing(24)
        self.optionen: dict[str, QCheckBox] = {}
        for i, (schl, text) in enumerate(OPTIONEN):
            k = QCheckBox(text); k.setChecked(getattr(s, schl))
            self.optionen[schl] = k
            g.addWidget(k, i // 2, i % 2)
        v.addWidget(_gruppe("Exportoptionen", g))
        v.addStretch(1)
        return w

    def _seiten_schalten(self, an: bool) -> None:
        for x in (self.von, self.bis, self.l_von, self.l_bis):
            x.setEnabled(an)

    def _durchsuchen(self) -> None:
        from lunivo_writer.ui.baukasten.speichern_fenster import datei_speichern
        neu = datei_speichern(self, "PDF-Datei exportieren", self.pfad.text().strip(), "PDF-Dokument (*.pdf)")
        if neu:                                                      # das Dateifenster hat vor dem Ersetzen schon gefragt
            self.pfad.setText(neu); self._ersetzen_ok = neu

    # ---- Berechtigungseinstellungen ----------------------------------------------------------------------------------
    def _rechte(self, s: PdfWahl) -> QWidget:
        w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(10, 10, 10, 10); v.setSpacing(10)
        self.verschluesseln = QCheckBox("Datei &verschlüsseln"); self.verschluesseln.setChecked(s.verschluesseln)
        v.addWidget(self.verschluesseln)
        self.innen = QWidget(); g = QGridLayout(self.innen); g.setContentsMargins(0, 0, 0, 0); g.setHorizontalSpacing(10); g.setVerticalSpacing(10)
        self.rechte_kw, self.rechte_kw2 = _kennwort(), _kennwort()
        self.rechte_kw.setText(s.kennwort_rechte); self.rechte_kw2.setText(s.kennwort_rechte)
        self._kennwort_zeile(g, 0, self.rechte_kw, self.rechte_kw2, "&Kennwort:", "Bes&tätigen:")
        hinweis = QLabel("Hinweis: Nur durch das Einrichten eines Kennworts können die nachstehenden Einstellungen in Kraft treten "
                         "und von anderen Benutzern nicht mehr geändert werden.")
        hinweis.setWordWrap(True); hinweis.setContentsMargins(30, 0, 0, 0)
        g.addWidget(hinweis, 1, 0, 1, 4)
        self.rechte: dict[str, QCheckBox] = {}
        for i, (schl, text) in enumerate(RECHTE):
            k = QCheckBox(text); k.setChecked(getattr(s, schl))
            self.rechte[schl] = k
            g.addWidget(k, 2 + i, 0, 1, 2)
        dl = QLabel("&Druckberechtigungen:")
        self.druck = QComboBox(); self.druck.setMinimumHeight(FELD_H)
        for text, wert in DRUCK:
            self.druck.addItem(text, wert)
        self.druck.setCurrentIndex(max(0, self.druck.findData(s.druck)))
        dl.setBuddy(self.druck)
        g.addWidget(dl, 2, 2, 1, 2); g.addWidget(self.druck, 3, 2, 1, 2)
        g.addWidget(QLabel("Kennwort zum Öffnen der Datei:"), 5, 0, 1, 4)
        self.oeffnen_kw, self.oeffnen_kw2 = _kennwort(), _kennwort()
        self.oeffnen_kw.setText(s.kennwort_oeffnen); self.oeffnen_kw2.setText(s.kennwort_oeffnen)
        self._kennwort_zeile(g, 6, self.oeffnen_kw, self.oeffnen_kw2, "K&ennwort:", "Best&ätigen:")
        g.setColumnStretch(1, 3); g.setColumnStretch(3, 2)
        v.addWidget(self.innen)
        v.addStretch(1)
        self.verschluesseln.toggled.connect(self.innen.setEnabled); self.innen.setEnabled(s.verschluesseln)
        return w

    @staticmethod
    def _kennwort_zeile(g: QGridLayout, zeile: int, feld: QLineEdit, bestaetigen: QLineEdit, text: str, text2: str) -> None:
        l1, l2 = QLabel(text), QLabel(text2)
        l1.setBuddy(feld); l2.setBuddy(bestaetigen)
        g.addWidget(l1, zeile, 0); g.addWidget(feld, zeile, 1); g.addWidget(l2, zeile, 2, Qt.AlignRight); g.addWidget(bestaetigen, zeile, 3)

    # ---- Ergebnis ----------------------------------------------------------------------------------------------------
    def ergebnis(self) -> PdfWahl:
        bereich = next(k for k, b in self._bereiche.items() if b.isChecked())
        w = PdfWahl(pfad=os.path.expanduser(self.pfad.text().strip()), bereich=bereich, von=self.von.value(), bis=self.bis.value(),
                    verschluesseln=self.verschluesseln.isChecked(), kennwort_rechte=self.rechte_kw.text(),
                    kennwort_oeffnen=self.oeffnen_kw.text(), druck=self.druck.currentData(), schliessen=self.schliessen.isChecked())
        for schl, k in {**self.optionen, **self.rechte}.items():
            setattr(w, schl, k.isChecked())
        return w

    def _ok(self) -> None:
        from PySide6.QtWidgets import QMessageBox
        w = self.ergebnis()
        fehler = ""
        if not w.pfad:
            fehler = "Bitte angeben, wo die PDF-Datei gespeichert werden soll."
        elif not os.path.isdir(os.path.dirname(w.pfad) or "."):
            fehler = f"Den Ordner „{os.path.dirname(w.pfad)}“ gibt es nicht."
        if fehler:
            self.reiter.setCurrentIndex(0)
        else:
            fehler = kennwort_fehler(w, self.rechte_kw2.text(), self.oeffnen_kw2.text())
            if fehler:
                self.reiter.setCurrentIndex(1)
        if fehler:
            QMessageBox.warning(self, self.windowTitle(), fehler)
            return
        if not w.pfad.lower().endswith(".pdf"):
            w.pfad += ".pdf"; self.pfad.setText(w.pfad)
        if os.path.exists(w.pfad) and w.pfad != self._ersetzen_ok and QMessageBox.question(
                self, self.windowTitle(), f"„{os.path.basename(w.pfad)}“ ist schon vorhanden. Möchten Sie die Datei ersetzen?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        self._wahl = w
        if not self._exportieren(w):
            return
        self._ersetzen_ok = w.pfad
        if w.schliessen:
            self.accept()
        else:
            self.meldung.setText(f"Exportiert: {w.pfad}")
            self.meldung.show()

    def wahl(self) -> PdfWahl | None:
        """Die zuletzt exportierte Wahl (auch wenn das Fenster danach mit „Abbrechen“ geschlossen wurde)."""
        return self._wahl


def pdf_export_fragen(parent, start: PdfWahl, seiten: int, aktuelle: int, markierung: bool,
                      exportieren: Callable[[PdfWahl], bool]) -> PdfWahl | None:
    """Zeigt das Fenster; ``exportieren`` schreibt bei jedem OK. → die zuletzt exportierte Wahl oder ``None``."""
    f = PdfExportFenster(parent, start, seiten, aktuelle, markierung, exportieren)
    f.exec()
    return f.wahl()
