"""Eingebettete, schrittweise PDF-Exportansicht für Lunivos Datei-Menü."""
from __future__ import annotations

import os
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QButtonGroup, QCheckBox, QComboBox, QGridLayout, QHBoxLayout, QLabel, QLayout,
                               QLineEdit, QMessageBox, QPushButton, QRadioButton, QSpinBox, QToolButton,
                               QVBoxLayout, QWidget)

from lunivo_writer.services.pdf_export import DRUCK, PdfWahl, kennwort_fehler

FELD_H = 34
RECHTE = [("aendern", "Ändern erlauben"), ("kopieren", "Kopieren erlauben"),
          ("kommentieren", "Kommentare hinzufügen erlauben")]


def _abschnitt(titel: str, hilfe: str, layout=None) -> QWidget:
    w = QWidget()
    v = QVBoxLayout(w); v.setContentsMargins(0, 8, 0, 8); v.setSpacing(5)
    kopf = QLabel(titel); kopf.setStyleSheet("font-weight: 600; font-size: 11pt;")
    erklaerung = QLabel(hilfe); erklaerung.setWordWrap(True); erklaerung.setObjectName("bsHinweis")
    v.addWidget(kopf); v.addWidget(erklaerung)
    if layout is not None:
        v.addLayout(layout) if isinstance(layout, QLayout) else v.addWidget(layout)
    return w


def _einklappen(titel: str, beschreibung: str, inhalt: QWidget, offen: bool = False) -> tuple[QWidget, QToolButton]:
    w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 4, 0, 4); v.setSpacing(4)
    knopf = QToolButton(); knopf.setText(titel); knopf.setCheckable(True); knopf.setChecked(offen)
    knopf.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); knopf.setArrowType(Qt.DownArrow if offen else Qt.RightArrow)
    knopf.setAutoRaise(True); knopf.setMinimumHeight(FELD_H)
    knopf.setAccessibleName(titel); knopf.setAccessibleDescription(beschreibung)
    inhalt.setVisible(offen)
    knopf.toggled.connect(inhalt.setVisible)
    knopf.toggled.connect(lambda an: knopf.setArrowType(Qt.DownArrow if an else Qt.RightArrow))
    v.addWidget(knopf); v.addWidget(inhalt)
    return w, knopf


def _kennwort() -> QLineEdit:
    f = QLineEdit(); f.setEchoMode(QLineEdit.Password); f.setMinimumHeight(FELD_H)
    return f


class PdfExportAnsicht(QWidget):
    """PDF-Export als dauerhaft sichtbare zweite Menüspalte, keine separates Dialogfenster."""

    def __init__(self, parent, start: PdfWahl, seiten: int, aktuelle: int, markierung: bool,
                 exportieren: Callable[[PdfWahl], bool], zurueck: Callable[[], None]):
        super().__init__(parent)
        self._exportieren = exportieren
        self._zurueck = zurueck
        self._ersetzen_ok = ""
        self._wahl: PdfWahl | None = None
        self.optionen: dict[str, QCheckBox] = {}
        self.rechte: dict[str, QCheckBox] = {}

        root = QVBoxLayout(self); root.setContentsMargins(30, 20, 30, 16); root.setSpacing(3)
        titel = QLabel("PDF exportieren"); titel.setObjectName("bsTitel")
        root.addWidget(titel)
        intro = QLabel("Wähle Speicherort und Seiten. Weitere Einstellungen kannst du bei Bedarf öffnen.")
        intro.setWordWrap(True); intro.setObjectName("bsHinweis"); root.addWidget(intro)

        self.pfad = QLineEdit(start.pfad); self.pfad.setMinimumHeight(FELD_H)
        self.pfad.setAccessibleName("PDF-Dateiname und Speicherort")
        self.pfad.setToolTip("Dateiname und Speicherort der PDF-Datei.")
        durch = QPushButton("Durchsuchen …"); durch.setMinimumHeight(FELD_H); durch.clicked.connect(self._durchsuchen)
        durch.setAccessibleDescription("Speicherort für die PDF-Datei auswählen.")
        datei_zeile = QHBoxLayout(); datei_zeile.addWidget(self.pfad, 1); datei_zeile.addWidget(durch)
        root.addWidget(_abschnitt("1. PDF speichern", "Dateiname und Speicherort", datei_zeile))

        bereich_layout = QVBoxLayout(); bereich_layout.setContentsMargins(0, 0, 0, 0); bereich_layout.setSpacing(3)
        self.b_alles = QRadioButton("Ganzes Dokument")
        self.b_aktuell = QRadioButton(f"Aktuelle Seite ({aktuelle})")
        self.b_markierung = QRadioButton("Nur die Markierung")
        self.b_markierung.setEnabled(markierung)
        if not markierung:
            self.b_markierung.setToolTip("Diese Auswahl ist verfügbar, sobald Text im Dokument markiert ist.")
        self.b_seiten = QRadioButton("Seitenbereich")
        self._bereiche = {"alles": self.b_alles, "aktuell": self.b_aktuell, "markierung": self.b_markierung, "seiten": self.b_seiten}
        gruppe = QButtonGroup(self)
        for b in self._bereiche.values():
            gruppe.addButton(b); bereich_layout.addWidget(b)
        bereich = start.bereich if start.bereich != "markierung" or markierung else "alles"
        self._bereiche.get(bereich, self.b_alles).setChecked(True)
        seiten_zeile = QHBoxLayout(); seiten_zeile.setContentsMargins(25, 0, 0, 0)
        self.von, self.bis = QSpinBox(), QSpinBox()
        for feld, wert in ((self.von, start.von), (self.bis, start.bis)):
            feld.setRange(1, max(1, seiten)); feld.setValue(min(max(1, wert), max(1, seiten)))
            feld.setMinimumHeight(FELD_H); feld.setMinimumWidth(90)
        if start.bereich != "seiten":
            self.von.setValue(1); self.bis.setValue(max(1, seiten))
        self.l_von, self.l_bis = QLabel("Von Seite"), QLabel("bis")
        self.l_von.setBuddy(self.von); self.l_bis.setBuddy(self.bis)
        seiten_zeile.addWidget(self.l_von); seiten_zeile.addWidget(self.von); seiten_zeile.addWidget(self.l_bis)
        seiten_zeile.addWidget(self.bis); seiten_zeile.addStretch(1)
        bereich_layout.addLayout(seiten_zeile)
        self.b_seiten.toggled.connect(self._seiten_schalten)
        self._seiten_schalten(self.b_seiten.isChecked())
        root.addWidget(_abschnitt("2. Seiten auswählen", "Lege fest, welche Seiten in die PDF kommen.", bereich_layout))

        inhalte = QVBoxLayout(); inhalte.setContentsMargins(0, 0, 0, 0); inhalte.setSpacing(3)
        for key, text, tip in (
            ("hyperlinks", "Links beibehalten", "Anklickbare Links im Dokument funktionieren auch im PDF."),
            ("kommentare", "Kommentare übernehmen", "Kommentare erscheinen im PDF als Notizen."),
            ("ueberschriften", "Überschriften als PDF-Lesezeichen", "Erstellt eine klickbare Navigation aus den Dokumentüberschriften."),
        ):
            box = QCheckBox(text); box.setChecked(getattr(start, key)); box.setToolTip(tip)
            self.optionen[key] = box; inhalte.addWidget(box)
        root.addWidget(_abschnitt("3. Inhalte übernehmen", "Wähle, was im PDF erhalten bleiben soll.", inhalte))

        weitere = QWidget(); av = QVBoxLayout(weitere); av.setContentsMargins(18, 2, 0, 2); av.setSpacing(3)
        for key, text, tip in (
            ("eigenschaften", "Dokumentinformationen übernehmen", "Titel, Verfasser und weitere Dokumentangaben in der PDF speichern."),
            ("textmarken", "Vorhandene Textmarken als Sprungziele übernehmen", "Gesetzte Textmarken werden im PDF anklickbar."),
            ("notenlinks", "Fuß- und Endnoten verknüpfen", "Notenzeichen führen im PDF zur jeweiligen Fuß- oder Endnote."),
            ("andere", "Weitere Formatvorlagen als Lesezeichen", "Zum Beispiel Titel, Untertitel oder Zitat in der PDF-Navigation anzeigen."),
            ("eigene", "Eigene Formatvorlagen als Lesezeichen", "Benutzerdefinierte Formatvorlagen in der PDF-Navigation anzeigen."),
        ):
            box = QCheckBox(text); box.setChecked(getattr(start, key)); box.setToolTip(tip)
            self.optionen[key] = box; av.addWidget(box)
        weitere_box, self.weitere_knopf = _einklappen("Weitere Exportoptionen", "Zusätzliche Angaben und Navigationsoptionen für die PDF.", weitere)
        root.addWidget(weitere_box)

        self.schutz_inhalt = self._schutz(start)
        schutz_box, self.schutz_knopf = _einklappen("4. Schutz und Berechtigungen", "Optionaler Kennwortschutz und Einstellungen dafür, was Empfänger mit der PDF dürfen.", self.schutz_inhalt)
        root.addWidget(schutz_box)

        self.meldung = QLabel(); self.meldung.setWordWrap(True); self.meldung.setObjectName("bsHinweis"); self.meldung.hide()
        root.addWidget(self.meldung)
        root.addStretch(1)

        fuss = QHBoxLayout(); fuss.setContentsMargins(0, 8, 0, 0)
        self.schliessen = QCheckBox("Nach dem Export zum Dokument zurückkehren")
        self.schliessen.setChecked(start.schliessen)
        self.schliessen.setToolTip("Kehrt nach erfolgreichem Export zur Dokumentbearbeitung zurück.")
        abbrechen = QPushButton("Zurück zum Dokument"); abbrechen.clicked.connect(self._zurueck)
        self.ok = QPushButton("PDF exportieren"); self.ok.setObjectName("optFertig"); self.ok.setDefault(True)
        self.ok.setCursor(Qt.PointingHandCursor); self.ok.setMinimumHeight(38); self.ok.clicked.connect(self._ok)
        fuss.addWidget(self.schliessen); fuss.addStretch(1); fuss.addWidget(abbrechen); fuss.addWidget(self.ok)
        root.addLayout(fuss)

    def _schutz(self, s: PdfWahl) -> QWidget:
        bereich = QWidget()
        v = QVBoxLayout(bereich); v.setContentsMargins(16, 2, 0, 4); v.setSpacing(6)
        self.verschluesseln = QCheckBox("PDF mit Kennwort schützen")
        self.verschluesseln.setChecked(s.verschluesseln)
        self.verschluesseln.setToolTip("Schützt den Zugriff und/oder legt fest, was andere Personen mit der PDF tun dürfen.")
        v.addWidget(self.verschluesseln)

        self.innen = QWidget(); g = QGridLayout(self.innen); g.setContentsMargins(20, 2, 0, 4); g.setHorizontalSpacing(10); g.setVerticalSpacing(7)
        self.rechte_kw, self.rechte_kw2 = _kennwort(), _kennwort()
        self.rechte_kw.setText(s.kennwort_rechte); self.rechte_kw2.setText(s.kennwort_rechte)
        self._kennwort_zeile(g, 0, self.rechte_kw, self.rechte_kw2, "Kennwort für Berechtigungen", "Bestätigung")
        self.rechte_kw.setAccessibleName("Kennwort für Berechtigungen"); self.rechte_kw2.setAccessibleName("Bestätigung des Berechtigungskennworts")
        hinweis = QLabel("Mit diesem Kennwort können Empfänger die unten gewählten Einschränkungen nicht ohne Weiteres ändern. Zum Öffnen der PDF ist es nicht erforderlich.")
        hinweis.setWordWrap(True); hinweis.setObjectName("bsHinweis"); g.addWidget(hinweis, 1, 0, 1, 4)

        self.rechte: dict[str, QCheckBox] = {}
        for row, (key, label) in enumerate(RECHTE, start=2):
            box = QCheckBox(label); box.setChecked(getattr(s, key)); self.rechte[key] = box
            g.addWidget(box, row, 0, 1, 2)
        druck_label = QLabel("Drucken"); self.druck = QComboBox(); self.druck.setMinimumHeight(FELD_H)
        for text, value in DRUCK:
            label = {"Freier Druck": "Drucken", "Nur niedrige Auflösung": "Drucken in niedriger Auflösung",
                     "Kein Druck": "Drucken nicht erlauben"}.get(text, text)
            self.druck.addItem(label, value)
        self.druck.setCurrentIndex(max(0, self.druck.findData(s.druck))); druck_label.setBuddy(self.druck)
        g.addWidget(druck_label, 2, 2); g.addWidget(self.druck, 3, 2, 1, 2)

        oeffnen_titel = QLabel("Kennwort zum Öffnen der PDF (optional)")
        oeffnen_titel.setToolTip("Wer dieses Kennwort nicht kennt, kann die PDF nicht öffnen.")
        g.addWidget(oeffnen_titel, 5, 0, 1, 4)
        self.oeffnen_kw, self.oeffnen_kw2 = _kennwort(), _kennwort()
        self.oeffnen_kw.setText(s.kennwort_oeffnen); self.oeffnen_kw2.setText(s.kennwort_oeffnen)
        self._kennwort_zeile(g, 6, self.oeffnen_kw, self.oeffnen_kw2, "Kennwort", "Bestätigung")
        self.oeffnen_kw.setAccessibleName("Kennwort zum Öffnen der PDF"); self.oeffnen_kw2.setAccessibleName("Bestätigung des Kennworts zum Öffnen")
        g.setColumnStretch(1, 3); g.setColumnStretch(3, 2)
        v.addWidget(self.innen)
        self.verschluesseln.toggled.connect(self.innen.setEnabled); self.innen.setEnabled(s.verschluesseln)
        return bereich

    @staticmethod
    def _kennwort_zeile(g: QGridLayout, row: int, feld: QLineEdit, bestaetigen: QLineEdit, text: str, text2: str) -> None:
        l1, l2 = QLabel(text), QLabel(text2)
        l1.setBuddy(feld); l2.setBuddy(bestaetigen)
        g.addWidget(l1, row, 0); g.addWidget(feld, row, 1); g.addWidget(l2, row, 2); g.addWidget(bestaetigen, row, 3)

    def _seiten_schalten(self, an: bool) -> None:
        for feld in (self.von, self.bis, self.l_von, self.l_bis):
            feld.setEnabled(an)

    def _durchsuchen(self) -> None:
        from lunivo_writer.ui.baukasten.speichern_fenster import datei_speichern
        neu = datei_speichern(self, "PDF-Datei exportieren", self.pfad.text().strip(), "PDF-Dokument (*.pdf)")
        if neu:
            self.pfad.setText(neu); self._ersetzen_ok = neu

    def ergebnis(self) -> PdfWahl:
        bereich = next(key for key, button in self._bereiche.items() if button.isChecked())
        w = PdfWahl(pfad=os.path.expanduser(self.pfad.text().strip()), bereich=bereich, von=self.von.value(), bis=self.bis.value(),
                    verschluesseln=self.verschluesseln.isChecked(), kennwort_rechte=self.rechte_kw.text(),
                    kennwort_oeffnen=self.oeffnen_kw.text(), druck=self.druck.currentData(), schliessen=self.schliessen.isChecked())
        for key, box in {**self.optionen, **self.rechte}.items():
            setattr(w, key, box.isChecked())
        return w

    def _ok(self) -> None:
        w = self.ergebnis()
        fehler = ""
        if not w.pfad:
            fehler = "Bitte gib einen Dateinamen und Speicherort für die PDF an."
        elif not os.path.isdir(os.path.dirname(w.pfad) or "."):
            fehler = f"Der gewählte Ordner „{os.path.dirname(w.pfad)}“ ist nicht vorhanden."
        if fehler:
            self.pfad.setFocus()
        elif w.verschluesseln:
            fehler = kennwort_fehler(w, self.rechte_kw2.text(), self.oeffnen_kw2.text())
            if fehler:
                self.schutz_knopf.setChecked(True)
                if fehler.startswith("Das Kennwort für die Berechtigungen"):
                    self.rechte_kw2.setFocus()
                else:
                    self.oeffnen_kw2.setFocus()
        if fehler:
            QMessageBox.warning(self, "PDF-Export", fehler)
            return
        if not w.pfad.lower().endswith(".pdf"):
            w.pfad += ".pdf"; self.pfad.setText(w.pfad)
        if os.path.exists(w.pfad) and w.pfad != self._ersetzen_ok and QMessageBox.question(
                self, "PDF ersetzen?", f"„{os.path.basename(w.pfad)}“ ist schon vorhanden. Möchtest du die Datei ersetzen?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return
        if not self._exportieren(w):
            return
        self._wahl = w; self._ersetzen_ok = w.pfad
        if w.schliessen:
            self._zurueck()
        else:
            self.meldung.setText(f"PDF gespeichert: {w.pfad}")
            self.meldung.show()

    def wahl(self) -> PdfWahl | None:
        return self._wahl
