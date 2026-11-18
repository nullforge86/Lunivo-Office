"""Referenzverwaltung für die ausgewählte Testdatei: Zuordnung von Referenz-PDF, Seitenbildern, Ursprungsprogramm, Version, Betriebssystem, Schriften und erwarteten Strukturen.

Zuordnungen entstehen nur durch ausdrückliche Handlung. Namensgleiche Dateien werden lediglich als **Vorschlag** angezeigt (nie automatisch verwendet); mehrere Kandidaten gelten als
„mehrdeutig“."""
from __future__ import annotations

import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPlainTextEdit, QPushButton, QSpinBox,
                               QVBoxLayout, QWidget)

PROGRAMME = ["", "Microsoft Word", "LibreOffice Writer", "ONLYOFFICE", "Andere"]


def erwartet_zu_text(d: dict) -> str:
    return "\n".join(f"{k}={v}" for k, v in d.items())


def text_zu_erwartet(text: str) -> tuple[dict, list[str]]:
    """``schluessel=zahl`` je Zeile. → (Werte, fehlerhafte Zeilen)"""
    aus, fehler = {}, []
    for z in text.splitlines():
        z = z.strip()
        if not z or z.startswith("#"):
            continue
        k, _, v = z.partition("=")
        try:
            aus[k.strip()] = int(v.strip())
        except ValueError:
            fehler.append(z)
    return aus, fehler


class ReferenzPanel(QWidget):
    gespeichert = Signal(int)

    def __init__(self, db, konfig_fn, parent=None):
        super().__init__(parent)
        self.db, self.konfig_fn = db, konfig_fn
        self.datei: dict | None = None
        self.vorschlag: dict | None = None
        self.kopf = QLabel("Keine Datei ausgewählt")
        self.kopf.setWordWrap(True)
        self.zustand = QLabel("")
        self.pdf, self.bilder = QLineEdit(), QLineEdit()
        self.programm = QComboBox()
        self.programm.setEditable(True)
        self.programm.addItems(PROGRAMME)
        self.version, self.system, self.schriften = QLineEdit(), QLineEdit(), QLineEdit()
        self.seiten = QSpinBox()
        self.seiten.setRange(0, 100000)
        self.seiten.setSpecialValueText("unbekannt")
        self.erwartet = QPlainTextEdit()
        self.erwartet.setPlaceholderText("Erwartete Strukturen, eine je Zeile, z. B.\nabsaetze=120\ntabellen=3\nbilder=2\nfussnoten=4\nfett_zeichen=850")
        self.erwartet.setMaximumHeight(110)
        self.notiz = QLineEdit()
        self.liste = QListWidget()
        self.liste.setMaximumHeight(80)
        form = QFormLayout()
        form.addRow("Referenz-PDF", self._mit_knopf(self.pdf, self._pdf_waehlen))
        form.addRow("Seitenbilder (Ordner)", self._mit_knopf(self.bilder, self._ordner_waehlen))
        form.addRow("Ursprungsprogramm", self.programm)
        form.addRow("Programmversion", self.version)
        form.addRow("Betriebssystem", self.system)
        form.addRow("Verwendete Schriften", self.schriften)
        form.addRow("Erwartete Seitenanzahl", self.seiten)
        form.addRow("Erwartete Strukturen (optional, für Fortgeschrittene)", self.erwartet)
        form.addRow("Notiz", self.notiz)
        speichern = QPushButton("Zuordnung speichern")
        speichern.clicked.connect(self.speichern)
        loeschen = QPushButton("Zuordnung entfernen")
        loeschen.clicked.connect(self.entfernen)
        suchen = QPushButton("Vorschläge suchen")
        suchen.clicked.connect(self.vorschlaege_suchen)
        uebernehmen = QPushButton("Gewählten Vorschlag übernehmen")
        uebernehmen.clicked.connect(self.vorschlag_uebernehmen)
        knoepfe = QHBoxLayout()
        for b in (speichern, loeschen):
            knoepfe.addWidget(b)
        knoepfe2 = QHBoxLayout()
        for b in (suchen, uebernehmen):
            knoepfe2.addWidget(b)
        lay = QVBoxLayout(self)
        lay.addWidget(self.kopf)
        lay.addWidget(self.zustand)
        lay.addLayout(form)
        lay.addLayout(knoepfe)
        lay.addWidget(QLabel("Namensgleiche Kandidaten (nur Vorschläge, bis sie übernommen werden):"))
        lay.addWidget(self.liste)
        lay.addLayout(knoepfe2)
        lay.addStretch(1)
        self.setEnabled(False)

    @staticmethod
    def _mit_knopf(feld: QLineEdit, fn) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        b = QPushButton("…")
        b.setFixedWidth(32)
        b.clicked.connect(fn)
        h.addWidget(feld, 1)
        h.addWidget(b)
        return w

    def _pdf_waehlen(self) -> None:
        p, _ = QFileDialog.getOpenFileName(self, "Referenz-PDF wählen", os.path.dirname(self.datei["pfad"]) if self.datei else "", "PDF (*.pdf)")
        if p:
            self.pdf.setText(p)

    def _ordner_waehlen(self) -> None:
        p = QFileDialog.getExistingDirectory(self, "Ordner mit Seitenbildern wählen", os.path.dirname(self.datei["pfad"]) if self.datei else "")
        if p:
            self.bilder.setText(p)

    # ---- Daten -----------------------------------------------------------------------------------------------------
    def zeige(self, datei: dict | None, vorschlag: dict | None = None) -> None:
        from kompatibilitaetspruefer.verwaltung.dateisuche import referenzzustand
        self.datei, self.vorschlag = datei, vorschlag
        self.setEnabled(datei is not None)
        self.liste.clear()
        if datei is None:
            self.kopf.setText("Keine Datei ausgewählt")
            self.zustand.setText("")
            return
        r = self.db.referenz(datei["id"]) or {}
        self.kopf.setText(f"<b>{datei['name']}</b><br><small>{datei['pfad']}</small>")
        self.pdf.setText(r.get("pdf", ""))
        self.bilder.setText(r.get("bilder", ""))
        self.programm.setCurrentText(r.get("programm") or datei.get("programm", ""))
        self.version.setText(r.get("programmversion", ""))
        self.system.setText(r.get("betriebssystem", ""))
        self.schriften.setText(r.get("schriften", ""))
        self.seiten.setValue(r.get("seiten_erwartet") or 0)
        self.erwartet.setPlainText(erwartet_zu_text(r.get("erwartet", {})))
        self.notiz.setText(r.get("notiz", ""))
        z = referenzzustand(datei["pfad"], r or None, vorschlag)
        text = {"zugeordnet": "Referenz zugeordnet.", "unvollstaendig": "Nur erwartete Werte, keine visuelle Referenz — die Layoutprüfung kann nicht vergleichen.",
                "vorschlag": "Ein namensgleicher Kandidat wurde gefunden (Vorschlag, noch nicht übernommen).",
                "mehrdeutig": "Mehrere Kandidaten — mehrdeutig. Bitte manuell zuordnen.", "fehlt": "Keine Referenz zugeordnet.",
                "defekt": "Die zugeordnete Referenzdatei existiert nicht mehr."}[z]
        self.zustand.setText(f"<b>Referenzstatus:</b> {text}")
        if vorschlag:
            for k in vorschlag["kandidaten"]:
                self.liste.addItem(k)

    def speichern(self) -> None:
        if self.datei is None:
            return
        erw, fehler = text_zu_erwartet(self.erwartet.toPlainText())
        if fehler:
            QMessageBox.warning(self, "Erwartete Strukturen", "Diese Zeilen sind nicht im Format „schluessel=zahl“:\n" + "\n".join(fehler[:8]))
            return
        pdf, bilder = self.pdf.text().strip(), self.bilder.text().strip()
        for pfad, ist_ordner in ((pdf, False), (bilder, True)):
            if pfad and not (os.path.isdir(pfad) if ist_ordner else os.path.isfile(pfad)):
                QMessageBox.warning(self, "Referenz", f"Nicht gefunden: {pfad}")
                return
        leer = not (pdf or bilder or erw or self.seiten.value() or self.programm.currentText() or self.version.text() or self.system.text() or self.schriften.text() or self.notiz.text())
        if leer:
            self.db.referenz_loeschen(self.datei["id"])
        else:
            self.db.referenz_setzen(self.datei["id"], {"pdf": pdf, "bilder": bilder, "programm": self.programm.currentText().strip(), "programmversion": self.version.text().strip(),
                                                      "betriebssystem": self.system.text().strip(), "schriften": self.schriften.text().strip(),
                                                      "seiten_erwartet": self.seiten.value() or None, "erwartet": erw, "notiz": self.notiz.text().strip()})
        self.gespeichert.emit(self.datei["id"])

    def entfernen(self) -> None:
        if self.datei is None:
            return
        self.db.referenz_loeschen(self.datei["id"])
        self.gespeichert.emit(self.datei["id"])
        self.zeige(self.datei, self.vorschlag)

    def vorschlaege_suchen(self) -> None:
        if self.datei is None:
            return
        from kompatibilitaetspruefer.verwaltung.dateisuche import referenzvorschlaege
        v = referenzvorschlaege(self.datei["pfad"], self.konfig_fn().referenzordner)
        self.zeige(self.datei, v)

    def vorschlag_uebernehmen(self) -> None:
        if self.datei is None or self.liste.currentItem() is None:
            QMessageBox.information(self, "Vorschlag", "Bitte zuerst einen Kandidaten in der Liste auswählen.")
            return
        pfad = self.liste.currentItem().text()
        if os.path.isdir(pfad):
            self.bilder.setText(pfad)
        else:
            self.pdf.setText(pfad)
        self.speichern()
