"""Hauptfenster des Lunivo Compatibility Testers.

Normaler Ablauf: Testdateien oder Ordner wählen → optional Referenz-PDFs hinzufügen (namensgleiche werden automatisch zugeordnet, mehrdeutige zur Bestätigung angezeigt) →
Prüfarten wählen → „Prüfung starten“ → Ergebnisse ansehen. Es müssen keine JSON-Dateien erstellt werden; alle internen Daten verwaltet SQLite.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys
import tempfile
import time
import traceback

from PySide6.QtCore import QThread, QTimer, Qt, Signal
from PySide6.QtGui import QAction, QGuiApplication, QKeySequence
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QGroupBox, QHBoxLayout, QInputDialog, QLabel, QMainWindow, QMessageBox,
                               QProgressBar, QPushButton, QScrollArea, QSplitter, QTableWidget, QTabWidget, QVBoxLayout, QWidget)

from kompatibilitaetspruefer import PROGRAMMNAME
from kompatibilitaetspruefer.oberflaeche.dateipanel import DateiPanel
from kompatibilitaetspruefer.oberflaeche.detailpanel import DetailPanel
from kompatibilitaetspruefer.oberflaeche.ergebnispanel import ErgebnisPanel
from kompatibilitaetspruefer.oberflaeche.konfigdialog import KonfigDialog
from kompatibilitaetspruefer.oberflaeche.referenzpanel import ReferenzPanel
from kompatibilitaetspruefer.oberflaeche.vergleichsansicht import Vergleichsansicht
from kompatibilitaetspruefer.pruefung import klassifikation as K
from kompatibilitaetspruefer.pruefung.pruefarten import verfuegbarkeit
from kompatibilitaetspruefer.verwaltung import dateisuche as DS
from kompatibilitaetspruefer.verwaltung import ergebnisexport
from kompatibilitaetspruefer.verwaltung import konfiguration as KF
from kompatibilitaetspruefer.verwaltung.datenbank import Datenbank
from kompatibilitaetspruefer.verwaltung.warteschlange import Warteschlange

EINZELARTEN = ("import", "struktur", "format", "layout", "export", "roundtrip")


class OrdnerLeser(QThread):
    """Liest einen Ordner im Hintergrund ein (große Sammlungen blockieren die Oberfläche nicht)."""
    fertig = Signal(list)

    def __init__(self, ordner: str, unterordner: bool, parent=None):
        super().__init__(parent)
        self.ordner, self.unterordner = ordner, unterordner

    def run(self) -> None:
        self.fertig.emit(DS.ordner_lesen(self.ordner, self.unterordner))


class ZuordnungsDialog(QDialog):
    """Mehrdeutige Referenzzuordnungen zur Bestätigung: je Datei die Kandidaten oder „keine“."""

    def __init__(self, eintraege: list[tuple[dict, list[str]]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mehrdeutige Referenzen bestätigen")
        self.resize(min(900, int(QGuiApplication.primaryScreen().availableGeometry().width() * 0.9)), 420)
        self.eintraege = eintraege
        self.tabelle = QTableWidget(len(eintraege), 2)
        self.tabelle.setHorizontalHeaderLabels(["Testdatei", "Referenz"])
        self.tabelle.horizontalHeader().setStretchLastSection(True)
        self.boxen: list[QComboBox] = []
        for r, (d, kand) in enumerate(eintraege):
            self.tabelle.setItem(r, 0, self._item(d["name"], d["pfad"]))
            box = QComboBox()
            box.addItem("— keine Referenz zuordnen —", "")
            for k in kand:
                box.addItem(k, k)
            self.boxen.append(box)
            self.tabelle.setCellWidget(r, 1, box)
        self.tabelle.setColumnWidth(0, 300)
        tasten = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        tasten.accepted.connect(self.accept)
        tasten.rejected.connect(self.reject)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Für diese Dateien gibt es mehrere mögliche Referenzen oder eine Referenz, die mehreren Dateien gleichen Namens zugeordnet werden könnte.\n"
                             "Wählen Sie die passende Referenz, oder lassen Sie die Datei ohne Referenz."))
        lay.addWidget(self.tabelle, 1)
        lay.addWidget(tasten)

    @staticmethod
    def _item(text: str, tip: str):
        from PySide6.QtWidgets import QTableWidgetItem
        i = QTableWidgetItem(text)
        i.setToolTip(tip)
        return i

    def auswahl(self) -> list[tuple[int, str]]:
        return [(d["id"], b.currentData()) for (d, _k), b in zip(self.eintraege, self.boxen) if b.currentData()]


class Hauptfenster(QMainWindow):
    def __init__(self, db: Datenbank, konfig: KF.Konfiguration):
        super().__init__()
        self.db, self.konfig = db, konfig
        self.setWindowTitle(PROGRAMMNAME)
        verfuegbar = QGuiApplication.primaryScreen().availableGeometry()          # nie größer als der nutzbare Bildschirm, damit die Titelleiste sichtbar bleibt
        breite, hoehe = min(1500, int(verfuegbar.width() * 0.92)), min(900, int(verfuegbar.height() * 0.85))
        self.resize(breite, hoehe)
        self.move(verfuegbar.x() + (verfuegbar.width() - breite) // 2, verfuegbar.y() + (verfuegbar.height() - hoehe) // 2)
        self.queue = Warteschlange(db, self)
        self._vorschlaege: dict[int, dict] = {}
        self._leser: OrdnerLeser | None = None
        self._vergleich_datei: int | None = None
        self._darstellung_wartet: int | None = None
        self._zeile: dict | None = None
        self._zustand = "bereit"
        self._stand: dict = {}
        self._ordner_offen: list[str] = []
        self.setAcceptDrops(True)
        self.dateien = DateiPanel()
        self.referenz = ReferenzPanel(db, lambda: self.konfig)
        self.ergebnisse = ErgebnisPanel()
        self.vergleich = Vergleichsansicht()
        self.details = DetailPanel()
        self._arten_gruppe()
        links = QSplitter(Qt.Vertical)
        links.addWidget(self.dateien)
        scroll = QScrollArea()                                                   # die Prüfarten dürfen bei kleinen Bildschirmen scrollen statt das Fenster zu vergrößern
        scroll.setWidget(self.arten_box)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(140)
        links.addWidget(scroll)
        links.setStretchFactor(0, 1)
        self.reiter = QTabWidget()
        self.reiter.addTab(self.ergebnisse, "Ergebnisse")
        self.reiter.addTab(self.vergleich, "Dokumentvergleich")
        self.reiter.addTab(self.referenz, "Referenzen")
        mitte = QSplitter(Qt.Horizontal)
        mitte.addWidget(links)
        mitte.addWidget(self.reiter)
        mitte.addWidget(self.details)
        mitte.setSizes([430, 900, 380])
        for w, mb in ((links, 220), (self.reiter, 300), (self.details, 200)):
            w.setMinimumWidth(mb)                                                 # explizite Mindestbreite statt der (großen) Layout-Vorgabe
        self.hilfsband = QLabel()                                                 # Statusband: Zustand (Bereit/läuft/abgebrochen/erfolgreich/Fehler) und nächster Schritt in einfachen Worten
        self.hilfsband.setWordWrap(True)
        self.hilfsband.setTextFormat(Qt.RichText)
        self.balken = QProgressBar()
        self.balken.setRange(0, 1)
        self.balken.setValue(0)
        self.balken.setTextVisible(True)
        self.balken.setVisible(False)
        aktionen = QHBoxLayout()
        aktionen.addWidget(self.start)
        aktionen.addWidget(self.stopp)
        aktionen.addWidget(self.neu_pruefung)
        aktionen.addStretch(1)
        zentrum = QWidget()
        zl = QVBoxLayout(zentrum)
        zl.setContentsMargins(6, 6, 6, 0)
        zl.setSpacing(6)
        zl.addLayout(aktionen)
        zl.addWidget(self.hilfsband)
        zl.addWidget(self.balken)
        zl.addWidget(mitte, 1)
        self.setCentralWidget(zentrum)
        self.setMinimumSize(min(900, int(verfuegbar.width() * 0.8)), min(560, int(verfuegbar.height() * 0.7)))   # Mindestgröße nie über dem Bildschirm
        self.setMaximumSize(verfuegbar.size())
        self._menues()
        self._statusleiste()
        self._verbinden()
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._aktualisieren)
        self.details.leeren()
        self.vergleich.leeren("Kein Ergebnis gewählt — Ergebnis doppelt anklicken oder „Darstellung erzeugen“")
        self._aktualisieren()
        self._zustand_setzen("bereit")

    # ---- Aufbau ----------------------------------------------------------------------------------------------------
    def _arten_gruppe(self) -> None:
        self.arten_box = QGroupBox("Prüfarten")
        l = QVBoxLayout(self.arten_box)
        self.art_boxen: dict[str, QCheckBox] = {}
        self.art_hinweis: dict[str, QLabel] = {}
        for a in EINZELARTEN + ("gesamt",):
            c = QCheckBox(K.PRUEFART_NAMEN[a])
            c.setChecked(a in self.konfig.aktive_arten)
            self.art_boxen[a] = c
            h = QLabel("")
            h.setWordWrap(True)
            h.setStyleSheet("color: gray; font-size: 11px; margin-left: 22px")
            self.art_hinweis[a] = h
            l.addWidget(c)
            l.addWidget(h)
        self.art_boxen["gesamt"].setToolTip("Kombiniert alle Prüfarten, soweit Referenzen und Schnittstellen vorhanden sind")
        self.art_boxen["gesamt"].toggled.connect(lambda an: [self.art_boxen[a].setEnabled(not an) for a in EINZELARTEN])
        self.start = QPushButton("▶  Prüfung starten")
        self.start.setObjectName("start")
        self.start.setMinimumHeight(36)
        self.start.setToolTip("Prüft die ausgewählten Dateien (ohne Auswahl: alle in der Liste)")
        self.stopp = QPushButton("■  Abbrechen")
        self.stopp.setMinimumHeight(36)
        self.stopp.setToolTip("Beendet die laufende Prüfung sofort")
        self.neu_pruefung = QPushButton("↺  Neue Prüfung")
        self.neu_pruefung.setMinimumHeight(36)
        self.neu_pruefung.setToolTip("Leert Dateiliste und Ergebnisse und beginnt von vorn (Ihre Dokumente bleiben unverändert)")
        self.setStyleSheet("QPushButton#start { font-weight: bold; padding: 4px 18px; background: #1f6feb; color: white; border-radius: 4px }"
                           "QPushButton#start:disabled { background: #a9b8cf; color: #eef2f8 }")
        self.neu = QCheckBox("Vorhandene Ergebnisse neu prüfen")
        self.neu.setToolTip("Ohne Haken werden Ergebnisse wiederverwendet, wenn Datei, Referenz, Einstellungen und Lunivo-Version unverändert sind")
        l.addWidget(self.neu)

    def _menues(self) -> None:
        mb = self.menuBar()

        def aktion(menue, text, fn, kurz=None, tip=""):
            a = QAction(text, self)
            a.triggered.connect(lambda *_: fn())
            if kurz:
                a.setShortcut(QKeySequence(kurz))
            if tip:
                a.setStatusTip(tip)
            menue.addAction(a)
            return a
        m = mb.addMenu("&Datei")
        aktion(m, "Dateien hinzufügen …", self.dateien_hinzufuegen, "Ctrl+O")
        aktion(m, "Ordner einlesen …", self.ordner_einlesen, "Ctrl+Shift+O")
        aktion(m, "Ausgewählte aus der Liste entfernen", self.entfernen, "Del")
        aktion(m, "Prüfliste leeren …", self.leeren)
        m.addSeparator()
        ex = m.addMenu("Ergebnisse exportieren")
        for fmt in ("csv", "json", "pdf"):
            aktion(ex, fmt.upper() + " …", lambda f=fmt: self.exportieren(f))
        m.addSeparator()
        aktion(m, "Beenden", self.close, "Ctrl+Q")
        m = mb.addMenu("&Prüfung")
        aktion(m, "Prüfung starten", self.starten, "F5")
        aktion(m, "Alle Dateien prüfen", lambda: self.starten(alle=True), "Ctrl+F5")
        aktion(m, "Neue Prüfung", self.neue_pruefung, "Ctrl+N")
        aktion(m, "Abbrechen", self.abbrechen, "Esc")
        m.addSeparator()
        aktion(m, "Darstellung erzeugen (Dokumentvergleich)", self.darstellung_erzeugen)
        m = mb.addMenu("&Referenzen")
        aktion(m, "Referenz-PDFs hinzufügen …", self.referenz_pdfs_hinzufuegen)
        aktion(m, "Referenz-Ordner mit PDFs hinzufügen …", self.referenz_ordner_hinzufuegen)
        aktion(m, "Referenzen automatisch zuordnen", lambda: self.auto_referenzen(self.dateien.alle_ids()))
        aktion(m, "Ursprungsprogramm der Auswahl setzen …", self.programm_setzen)
        m = mb.addMenu("&Einstellungen")
        aktion(m, "Konfiguration …", self.konfiguration, "Ctrl+,")
        m = mb.addMenu("&Hilfe")
        aktion(m, "So funktioniert das Programm …", self.hilfe_zeigen, "F1")

    def _statusleiste(self) -> None:
        self.fortschritt = QLabel("Bereit")
        self.statusBar().addWidget(self.fortschritt, 1)

    def _verbinden(self) -> None:
        self.dateien.hinzufuegen.connect(self.dateien_hinzufuegen)
        self.dateien.ordner.connect(self.ordner_einlesen)
        self.dateien.entfernen.connect(self.entfernen)
        self.dateien.leeren.connect(self.leeren)
        self.dateien.auswahl_geaendert.connect(self._datei_gewaehlt)
        self.referenz.gespeichert.connect(lambda _id: self._bald())
        self.ergebnisse.gewaehlt.connect(self._ergebnis_gewaehlt)
        self.ergebnisse.vergleich_gewuenscht.connect(self._zeige_vergleich)
        self.details.vergleich.connect(lambda: self._zeige_vergleich(self._zeile) if self._zeile else None)
        self.vergleich.darstellung_gewuenscht.connect(self.darstellung_erzeugen)
        self.start.clicked.connect(lambda: self.starten())
        self.stopp.clicked.connect(self.abbrechen)
        self.neu_pruefung.clicked.connect(self.neue_pruefung)
        self.queue.fortschritt.connect(self._fortschritt)
        self.queue.ergebnis_fertig.connect(self._ergebnis_fertig)
        self.queue.beendet.connect(self._beendet)

    # ---- Dateiverwaltung -------------------------------------------------------------------------------------------
    def dateien_hinzufuegen(self) -> None:
        endungen = " ".join("*" + e for e in sorted(DS.lesbare_endungen()))
        pfade, _ = QFileDialog.getOpenFileNames(self, "Testdateien wählen", os.path.expanduser(self.konfig.testordner) if os.path.isdir(os.path.expanduser(self.konfig.testordner)) else "",
                                                f"Unterstützte Dokumente ({endungen});;Alle Dateien (*)")
        self._hinzufuegen(pfade)

    def ordner_einlesen(self) -> None:
        start = os.path.expanduser(self.konfig.testordner)
        ordner = QFileDialog.getExistingDirectory(self, "Ordner mit Testdateien wählen", start if os.path.isdir(start) else "")
        if ordner:
            self._ordner_lesen(ordner)

    def _ordner_lesen(self, ordner: str) -> None:
        self._ordner_offen.append(ordner)
        self._ordner_naechster()

    def _ordner_naechster(self) -> None:
        if self._leser is not None or not self._ordner_offen:
            return
        ordner = self._ordner_offen.pop(0)
        self.fortschritt.setText(f"Ordner wird eingelesen: {ordner} …")
        self._leser = OrdnerLeser(ordner, self.konfig.unterordner, self)
        self._leser.fertig.connect(self._ordner_fertig)
        self._leser.start()
        self._tasten_aktualisieren()

    def _ordner_fertig(self, pfade: list) -> None:
        leser, self._leser = self._leser, None
        if leser is not None:
            leser.wait()
        self._hinzufuegen(pfade)
        self._ordner_naechster()
        self._tasten_aktualisieren()

    # ---- Ziehen und Ablegen ----------------------------------------------------------------------------------------
    def dragEnterEvent(self, ev) -> None:
        if ev.mimeData().hasUrls():
            ev.acceptProposedAction()

    def dropEvent(self, ev) -> None:
        pfade = [u.toLocalFile() for u in ev.mimeData().urls() if u.isLocalFile()]
        ordner = [p for p in pfade if os.path.isdir(p)]
        pdfs = [p for p in pfade if p.lower().endswith(".pdf") and os.path.isfile(p)]
        dateien = [p for p in pfade if os.path.isfile(p) and p not in pdfs]
        ev.acceptProposedAction()
        if dateien:
            self._hinzufuegen(dateien)
        for o in ordner:
            self._ordner_lesen(o)
        if pdfs:
            self.auto_referenzen(self.dateien.alle_ids(), pdfs)

    def _hinzufuegen(self, pfade: list[str]) -> None:
        if not pfade:
            self.fortschritt.setText("Keine Dateien gefunden")
            return
        if self._zustand != "laeuft":
            self._zustand_setzen("bereit")
        vorher = {d["id"] for d in self.db.dateien()}
        neu = self.db.dateien_hinzufuegen(pfade)
        ids = [d["id"] for d in self.db.dateien() if d["id"] not in vorher]
        nicht = [p for p in pfade if DS.format_zustand(os.path.splitext(p)[1]) != "unterstuetzt"]
        self.fortschritt.setText(f"{neu} Dateien hinzugefügt ({len(pfade) - neu} schon vorhanden)" + (f"; {len(nicht)} mit nicht unterstütztem Format (gekennzeichnet)" if nicht else ""))
        self._aktualisieren()
        self.auto_referenzen(ids)

    def entfernen(self) -> None:
        ids = self.dateien.ausgewaehlte_ids()
        if ids:
            self.db.dateien_entfernen(ids)
            self._aktualisieren()

    def leeren(self) -> None:
        if not self.dateien.alle_ids():
            return
        if QMessageBox.question(self, "Prüfliste leeren", "Alle Dateien samt Ergebnissen und Referenzzuordnungen aus der Prüfliste entfernen?\n(Die Dokumente selbst bleiben unverändert.)") == QMessageBox.Yes:
            self.db.dateien_leeren()
            self._aktualisieren()

    def programm_setzen(self) -> None:
        ids = self.dateien.ausgewaehlte_ids()
        if not ids:
            return
        name, ok = QInputDialog.getItem(self, "Ursprungsprogramm", "Mit welchem Programm entstanden die ausgewählten Dokumente?",
                                        ["", "Microsoft Word", "LibreOffice Writer", "ONLYOFFICE", "Andere"], 0, True)
        if ok:
            self.db.programm_setzen(ids, name.strip())
            self._aktualisieren()

    # ---- Referenzen ------------------------------------------------------------------------------------------------
    def referenz_pdfs_hinzufuegen(self) -> None:
        pfade, _ = QFileDialog.getOpenFileNames(self, "Referenz-PDFs wählen (aus Word, LibreOffice oder ONLYOFFICE erzeugt)", "", "PDF (*.pdf)")
        if pfade:
            self.auto_referenzen(self.dateien.alle_ids(), pfade)

    def referenz_ordner_hinzufuegen(self) -> None:
        ordner = QFileDialog.getExistingDirectory(self, "Ordner mit Referenz-PDFs wählen (Unterordner werden mitgelesen)", os.path.expanduser(self.konfig.referenzordner or ""))
        if not ordner:
            return
        pdfs = []
        for wurzel, dirs, namen in os.walk(ordner, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith("."))
            pdfs += [os.path.join(wurzel, n) for n in sorted(namen) if n.lower().endswith(".pdf")]
        if not pdfs:
            QMessageBox.information(self, "Referenz-Ordner", "In diesem Ordner wurden keine PDF-Dateien gefunden.")
            return
        self.auto_referenzen(self.dateien.alle_ids(), pdfs)

    def auto_referenzen(self, ids: list[int], zusatz_pdfs: list[str] | None = None) -> None:
        """Sichere Zuordnungen (genau ein Kandidat gleichen Namens, nicht mehrfach beansprucht) werden gesetzt; mehrdeutige werden zur Bestätigung angezeigt."""
        refs = self.db.alle_referenzen()
        kandidaten = [d for d in (self.db.datei(i) for i in ids) if d and not (refs.get(d["id"], {}).get("pdf") or refs.get(d["id"], {}).get("bilder"))
                      and DS.format_zustand(d["endung"]) == "unterstuetzt"]
        if not kandidaten:
            return
        erg = DS.automatisch_zuordnen(kandidaten, self.konfig.referenzordner, zusatz_pdfs)
        for datei_id, pfad in erg["eindeutig"]:
            self._referenz_setzen(datei_id, pfad, "automatisch zugeordnet (identischer Dateiname)")
        bestaetigt = 0
        if erg["mehrdeutig"]:
            lookup = {d["id"]: d for d in kandidaten}
            dlg = ZuordnungsDialog([(lookup[i], k) for i, k in erg["mehrdeutig"]], self)
            if dlg.exec() == QDialog.Accepted:
                for datei_id, pfad in dlg.auswahl():
                    self._referenz_setzen(datei_id, pfad, "vom Benutzer bestätigt")
                    bestaetigt += 1
        self.fortschritt.setText(f"Vergleichs-PDFs: {len(erg['eindeutig'])} automatisch gefunden (gleicher Dateiname), {bestaetigt} von Ihnen bestätigt, "
                                 f"{len(erg['mehrdeutig']) - bestaetigt} noch unklar, {len(erg['fehlt'])} ohne PDF (diese werden nur auf ihre Struktur geprüft)")
        self._aktualisieren()

    def _referenz_setzen(self, datei_id: int, pfad: str, notiz: str) -> None:
        r = self.db.referenz(datei_id) or {}
        r["notiz"] = (r.get("notiz", "") + " " + notiz).strip()
        r["bilder" if os.path.isdir(pfad) else "pdf"] = pfad
        self.db.referenz_setzen(datei_id, r)

    # ---- Prüfung ---------------------------------------------------------------------------------------------------
    def _gewaehlte_arten(self) -> list[str]:
        if self.art_boxen["gesamt"].isChecked():
            return list(EINZELARTEN)
        return [a for a in EINZELARTEN if self.art_boxen[a].isChecked()]

    def starten(self, alle: bool = False) -> None:
        if self.queue.laeuft or self._leser is not None:                          # kein zweiter Start: still ignorieren (die Taste ist in diesem Zustand ohnehin gesperrt)
            return
        arten = self._gewaehlte_arten()
        if not arten:
            QMessageBox.information(self, "Prüfung", "Bitte mindestens eine Prüfart auswählen.")
            return
        ids = self.dateien.alle_ids() if alle else (self.dateien.ausgewaehlte_ids() or self.dateien.sichtbare_ids())
        if not ids:
            QMessageBox.information(self, "Prüfung", "Die Prüfliste ist leer. Bitte Dateien oder einen Ordner hinzufügen.")
            return
        self.konfig.aktive_arten = [a for a in EINZELARTEN if a in arten]
        KF.speichern(self.konfig)
        refs = self.db.alle_referenzen()
        auftraege = []
        for d in self.dateien.zeilen_mit_id(ids):
            zustand = d["format_zustand"]
            ok_arten = []
            for a in arten:
                ok, grund = verfuegbarkeit(a, d["endung"], refs.get(d["id"]), zustand)
                if ok:
                    ok_arten.append(a)
                else:                                                     # nicht verfügbar: ausdrücklich als nicht prüfbar vermerken, nie still übergehen
                    self.db.ergebnis_speichern(d["id"], a, {"status": K.NICHT_PRUEFBAR, "fehlerart": "Nicht unterstützte Eigenschaft", "schwere": "hinweis", "beschreibung": grund,
                                                            "befunde": [K.nicht_unterstuetzt("Prüfart", grund)]})
            if ok_arten:
                auftraege.append((d["id"], ok_arten))
        self._stand = {}
        lauf = self.queue.starten(self.konfig, auftraege, self.neu.isChecked())
        self._aktualisieren()
        self.reiter.setCurrentWidget(self.ergebnisse)
        if lauf is None:
            self._zustand_setzen("erfolgreich", "<b>Nichts Neues zu prüfen.</b> Für alle gewählten Dateien liegen bereits aktuelle Ergebnisse vor "
                                 "(oder die Prüfarten sind nicht verfügbar). Mit „Vorhandene Ergebnisse neu prüfen“ erzwingen Sie eine neue Prüfung.")
        else:
            self._zustand_setzen("laeuft")

    def abbrechen(self) -> None:
        self.queue.abbrechen()

    def darstellung_erzeugen(self) -> None:
        ids = self.dateien.ausgewaehlte_ids() or ([self._vergleich_datei] if self._vergleich_datei else [])
        if not ids:
            QMessageBox.information(self, "Darstellung", "Bitte zuerst eine Datei auswählen.")
            return
        if self.queue.laeuft:
            QMessageBox.information(self, "Darstellung", "Es läuft bereits eine Prüfung. Bitte danach erneut versuchen.")
            return
        self._darstellung_wartet = ids[0]
        self.queue.starten(self.konfig, [(ids[0], ["darstellung"])], True)

    # ---- Rückmeldungen ---------------------------------------------------------------------------------------------
    def _fortschritt(self, s: dict) -> None:
        self._stand = s
        laeuft = s["laeuft"]
        self.balken.setRange(0, max(1, s["gesamt"]))
        self.balken.setValue(min(s["fertig"], max(1, s["gesamt"])))
        self.balken.setFormat(f"%v von {s['gesamt']} Dateien")
        if laeuft:
            if s.get("abbrechend"):
                self._zustand_setzen("abbrechend")
            else:
                self._zustand_setzen("laeuft")
        self._tasten_aktualisieren()
        self._bald()

    def _beendet(self, wie: str) -> None:
        s = self._stand
        if wie == "abgebrochen":
            self._zustand_setzen("abgebrochen")
        elif s.get("fehlgeschlagen"):
            self._zustand_setzen("fehler")
        else:
            self._zustand_setzen("erfolgreich")
        self._aktualisieren()

    def _ergebnis_fertig(self, datei_id: int) -> None:
        if self._darstellung_wartet == datei_id:
            self._darstellung_wartet = None
            self._vergleich_fuer_datei(datei_id)
            self.reiter.setCurrentWidget(self.vergleich)

    def _bald(self) -> None:
        if not self._timer.isActive():
            self._timer.start(1200 if self.queue.laeuft else 150)

    def _aktualisieren(self) -> None:
        dateien = self.db.dateien()
        refs = self.db.alle_referenzen()
        referenz = {d["id"]: DS.referenzzustand(d["pfad"], refs.get(d["id"]), self._vorschlaege.get(d["id"])) for d in dateien}
        stati = self.db.dateistatus()
        self.dateien.setze(dateien, stati, referenz)
        self.ergebnisse.setze(dateien, stati, self.db.ergebniszeilen())
        if self._zustand == "bereit":
            self._zustand_setzen("bereit")
        self._tasten_aktualisieren()

    _FARBEN = {"bereit": ("#eaf3ff", "#12263f", "#9cc2f0"), "laeuft": ("#fff6dd", "#4a3600", "#e8c766"), "abbrechend": ("#fff6dd", "#4a3600", "#e8c766"),
               "abgebrochen": ("#f0f0f0", "#2b2b2b", "#b5b5b5"), "erfolgreich": ("#e6f6e9", "#0f3d1a", "#8fd19e"), "fehler": ("#fde8e8", "#5a1212", "#e49a9a")}
    _NAMEN = {"bereit": "Bereit", "laeuft": "Prüfung läuft", "abbrechend": "Wird abgebrochen", "abgebrochen": "Prüfung abgebrochen", "erfolgreich": "Prüfung abgeschlossen",
              "fehler": "Prüfung mit Fehlern beendet"}

    def _zustand_setzen(self, zustand: str, text: str = "") -> None:
        """Einziger Ort, der Statusband, Fortschrittsanzeige und Tastenzustand setzt: Bereit · Prüfung läuft · Wird abgebrochen · Abgebrochen · Erfolgreich · Fehler."""
        self._zustand = zustand
        bg, fg, rand = self._FARBEN[zustand]
        self.hilfsband.setStyleSheet(f"background: {bg}; color: {fg}; border: 1px solid {rand}; border-radius: 4px; padding: 6px 10px")
        self.balken.setVisible(zustand in ("laeuft", "abbrechend"))
        if not text:
            text = self._standardtext(zustand)
        self.hilfsband.setText(text if zustand == "bereit" else f"<b>{self._NAMEN[zustand]}.</b> {text}")
        self._tasten_aktualisieren()

    def _standardtext(self, zustand: str) -> str:
        s = self._stand
        if zustand == "bereit":
            return self._bereit_text()
        gesamt, fertig = s.get("gesamt", 0), s.get("fertig", 0)
        if zustand == "laeuft":
            aktuell = ", ".join(s.get("aktuell", [])[:3])
            return f"{fertig} von {gesamt} Dateien geprüft" + (f" · gerade: {aktuell}" if aktuell else "") + (f" · {s.get('wiederverwendet', 0)} bereits aktuell" if s.get("wiederverwendet") else "")
        if zustand == "abbrechend":
            return "Laufende Prüfungen werden beendet …"
        if zustand == "abgebrochen":
            return f"{fertig} von {gesamt} Dateien wurden vollständig geprüft; die übrigen wurden nicht geprüft. Die Ergebnisse bis zum Abbruch bleiben sichtbar."
        n = self._zusammenfassung()
        if zustand == "fehler":
            return f"Bei {s.get('fehlgeschlagen', 0)} von {gesamt} Dateien war keine Prüfung möglich (z. B. beschädigt oder zu groß). {n}"
        return f"Alle {gesamt} Dateien wurden geprüft. {n} Einzelheiten: Reiter „Ergebnisse“, Doppelklick auf eine Zeile."

    def _zusammenfassung(self) -> str:
        stati = self.db.dateistatus()
        zaehler: dict[str, int] = {}
        for v in stati.values():
            g = K.gesamt_status(v)
            zaehler[g] = zaehler.get(g, 0) + 1
        return " · ".join(f"{n} {K.STATUS_NAMEN.get(g, g)}" for g, n in zaehler.items())

    def _bereit_text(self) -> str:
        dateien = self.db.dateien()
        n = len(dateien)
        if n == 0:
            return ("<b>Bereit.</b> <b>Schritt 1:</b> Ziehen Sie Dokumente oder einen Ordner in dieses Fenster – oder klicken Sie links auf <b>„📁 Ordner“</b> bzw. <b>„＋ Dateien“</b>.<br>"
                    "Tipp: Liegt neben einem Dokument ein <b>PDF mit gleichem Namen</b> (z. B. <i>Brief.docx</i> und <i>Brief.pdf</i>), erkennt das Programm es "
                    "<b>automatisch</b> und vergleicht Ihr Dokument damit. Mehr: <b>Hilfe → So funktioniert das Programm</b> (F1).")
        refs = self.db.alle_referenzen()
        referenz = {d["id"]: DS.referenzzustand(d["pfad"], refs.get(d["id"]), self._vorschlaege.get(d["id"])) for d in dateien}
        mit = sum(1 for v in referenz.values() if v == "zugeordnet")
        offen = sum(1 for v in referenz.values() if v in ("mehrdeutig", "vorschlag"))
        teile = [f"<b>Bereit.</b> {n} Dokumente in der Liste, {mit} mit Vergleichs-PDF, {n - mit} ohne."]
        if offen:
            teile.append(f"Bei {offen} ist unklar, welches PDF gemeint ist – siehe Menü <b>Referenzen → Referenzen automatisch zuordnen</b>.")
        elif n - mit:
            teile.append("Ohne PDF wird nur die Struktur geprüft; PDFs ergänzen Sie über <b>Referenzen</b> oder per Ziehen ins Fenster.")
        teile.append("<b>Schritt 2:</b> Auf <b>„▶ Prüfung starten“</b> klicken (Prüfarten links unten – die Vorgabe passt meist).")
        return " ".join(teile)

    def _tasten_aktualisieren(self) -> None:
        """Tasten folgen dem Zustand: nichts ist klickbar, was gerade nicht sinnvoll ist."""
        laeuft = self.queue.laeuft
        liest = self._leser is not None
        hat = bool(self.dateien.alle_ids())
        abbrechend = self._zustand == "abbrechend"
        self.start.setEnabled(hat and not laeuft and not liest)
        self.stopp.setEnabled(laeuft and not abbrechend)
        self.neu_pruefung.setEnabled((hat or self._zustand != "bereit") and not laeuft)
        self.arten_box.setEnabled(not laeuft)

    def neue_pruefung(self) -> None:
        """Alles zurücksetzen und von vorn beginnen. Dokumente und exportierte Dateien bleiben unberührt."""
        if self.queue.laeuft or self._leser is not None:
            return
        if self.db.ergebniszeilen() and QMessageBox.question(self, "Neue Prüfung", "Dateiliste und Ergebnisse verwerfen und neu beginnen?\n"
                                                              "(Ihre Dokumente und bereits exportierte Ergebnisse bleiben unverändert.)") != QMessageBox.Yes:
            return
        self._sitzung_leeren()
        self._aktualisieren()
        self._zustand_setzen("bereit")
        self.fortschritt.setText("Bereit")

    def _sitzung_leeren(self) -> None:
        self.db.sitzung_zuruecksetzen()
        _temporaeres_aufraeumen()
        self.queue.darstellungen.clear()
        self._vorschlaege.clear()
        self._stand, self._zeile, self._vergleich_datei, self._darstellung_wartet = {}, None, None, None
        self._ordner_offen.clear()
        self.dateien.suche.clear()
        for c in (self.dateien.f_format, self.dateien.f_status, self.dateien.f_ref, self.dateien.f_prog):
            c.setCurrentIndex(0)
        self.details.leeren()
        self.referenz.zeige(None, None)
        self._arten_verfuegbarkeit(None)
        self.vergleich.leeren("Kein Ergebnis gewählt — Ergebnis doppelt anklicken oder „Darstellung erzeugen“")
        self.balken.setValue(0)

    def hilfe_zeigen(self) -> None:
        QMessageBox.information(self, "So funktioniert das Programm",
                                "<b>Wozu dient das Programm?</b><br>Es prüft, ob Ihre Dokumente in Lunivo genauso aussehen und sich genauso verhalten wie im ursprünglichen Programm "
                                "(Word, LibreOffice, ONLYOFFICE).<br><br>"
                                "<b>1. Dokumente wählen</b><br>Links auf „Ordner“ oder „Dateien“ klicken. Es werden nur Dateien übernommen, die Lunivo lesen kann.<br><br>"
                                "<b>2. Vergleichs-PDFs (Referenzen)</b><br>Für einen Seitenvergleich braucht das Programm ein PDF, das im Ursprungsprogramm aus demselben Dokument erzeugt wurde. "
                                "Es sucht <b>automatisch</b> nach PDFs mit <b>gleichem Dateinamen</b> (ohne Endung) neben dem Dokument, im Referenzordner und unter den von Ihnen hinzugefügten PDFs. "
                                "Ist genau eins vorhanden, wird es zugeordnet; bei mehreren fragt das Programm nach. Andere PDFs fügen Sie über das Menü „Referenzen“ hinzu oder ordnen sie im Reiter „Referenzen“ zu.<br>"
                                "PDFs selbst werden nicht geprüft, sie dienen nur als Vorlage. Ohne PDF wird nur die Struktur des Dokuments geprüft.<br><br>"
                                "<b>3. Prüfen</b><br>Prüfarten wählen (die Vorgabe passt meist) und „Prüfung starten“ klicken. Ohne Auswahl in der Liste werden alle Dokumente geprüft.<br><br>"
                                "<b>4. Ergebnisse</b><br>Im Reiter „Ergebnisse“ sehen Sie je Dokument, ob es bestanden hat. Doppelklick zeigt Einzelheiten und den Seitenvergleich. "
                                "Über „Datei → Ergebnisse exportieren“ speichern Sie die Liste als CSV, JSON oder PDF.")

    # ---- Auswahl und Detail ----------------------------------------------------------------------------------------
    def _datei_gewaehlt(self, ids: list[int]) -> None:
        d = self.db.datei(ids[0]) if ids else None
        self.referenz.zeige(d, self._vorschlaege.get(d["id"]) if d else None)
        self._arten_verfuegbarkeit(d)
        if d is not None and len(ids) == 1 and self.reiter.currentWidget() is self.vergleich:
            self._vergleich_fuer_datei(d["id"])

    def _arten_verfuegbarkeit(self, d: dict | None) -> None:
        ref = self.db.referenz(d["id"]) if d else None
        for a in EINZELARTEN:
            c, h = self.art_boxen[a], self.art_hinweis[a]
            if d is None:
                h.setText("")
                c.setEnabled(not self.art_boxen["gesamt"].isChecked())
                continue
            ok, grund = verfuegbarkeit(a, d["endung"], ref, DS.format_zustand(d["endung"]))
            h.setText(("nicht verfügbar: " if not ok else "eingeschränkt: ") + grund if grund else "")
            c.setEnabled(ok and not self.art_boxen["gesamt"].isChecked())

    def _ergebnis_gewaehlt(self, zeile: dict) -> None:
        self._zeile = zeile
        e = self.db.ergebnis(zeile["ergebnis_id"])
        if e is None:
            self.details.leeren()
            return
        self.details.zeige(zeile, e, self.db.befunde(e["id"]), self.db.referenz(zeile["datei_id"]))

    def _zeige_vergleich(self, zeile: dict) -> None:
        if not zeile:
            return
        e = self.db.ergebnis(zeile["ergebnis_id"])
        bilder = json.loads(e["bilder_json"] or "{}") if e else {}
        if zeile["art"] == "layout" and bilder.get("lunivo"):
            self._setze_vergleich(zeile["datei_id"], zeile["name"], bilder, json.loads(e["werte_json"] or "{}").get("seitenwerte", []), zeile.get("seite"))
        else:
            self._vergleich_fuer_datei(zeile["datei_id"])
        self.reiter.setCurrentWidget(self.vergleich)

    def _vergleich_fuer_datei(self, datei_id: int) -> None:
        d = self.db.datei(datei_id)
        if d is None:
            return
        for e in self.db.ergebnisse_von(datei_id):
            if e["art"] == "layout":
                bilder = json.loads(e["bilder_json"] or "{}")
                if bilder.get("lunivo"):
                    self._setze_vergleich(datei_id, d["name"], bilder, json.loads(e["werte_json"] or "{}").get("seitenwerte", []), None)
                    return
        bilder = self.queue.darstellungen.get(datei_id)
        if bilder and bilder.get("lunivo"):
            self._setze_vergleich(datei_id, d["name"], bilder, [], None, "Darstellung ohne Beurteilung (keine Layoutprüfung mit Referenz) — keine Abweichungsmarkierungen")
            return
        self._vergleich_datei = datei_id
        self.vergleich.leeren(f"{d['name']}: noch keine Darstellung vorhanden — „Darstellung erzeugen“ oder eine Layoutprüfung mit Referenz starten")

    def _setze_vergleich(self, datei_id: int, name: str, bilder: dict, seitenwerte: list, seite, hinweis: str = "") -> None:
        self._vergleich_datei = datei_id
        ref = [p for p in bilder.get("referenz", []) if os.path.isfile(p)]
        lun = [p for p in bilder.get("lunivo", []) if os.path.isfile(p)]
        if not lun:
            self.vergleich.leeren(f"{name}: die Bilder liegen nicht mehr im Zwischenspeicher — „Darstellung erzeugen“ klicken")
            return
        quelle = "PDF" if bilder.get("referenz_quelle") == "pdf" else "Seitenbilder" if bilder.get("referenz_quelle") else "ohne Referenz"
        self.vergleich.setze(f"{name} — Referenz: {quelle}", ref, lun, seitenwerte, seite, hinweis or ("" if ref else "Keine Referenzdarstellung zugeordnet — nur die Lunivo-Seiten werden gezeigt"))

    # ---- Export, Konfiguration -------------------------------------------------------------------------------------
    def exportieren(self, fmt: str) -> None:
        zeilen = self.ergebnisse.sichtbare_ergebnisse()
        if not zeilen:
            QMessageBox.information(self, "Export", "Es gibt keine Ergebnisse zu exportieren.")
            return
        start = os.path.join(KF.ergebnisordner(self.konfig), f"ergebnisse.{fmt}")
        pfad, _ = QFileDialog.getSaveFileName(self, f"Ergebnisse als {fmt.upper()} exportieren", start, f"{fmt.upper()} (*.{fmt})")
        if not pfad:
            return
        try:
            n = ergebnisexport.exportiere(self.db, pfad, fmt, zeilen)
        except (OSError, ValueError) as e:
            QMessageBox.warning(self, "Export", f"Der Export ist fehlgeschlagen: {e}")
            return
        self.fortschritt.setText(f"{n} Ergebnisse nach {pfad} exportiert (aktuelle Filter berücksichtigt)")

    def konfiguration(self) -> None:
        dlg = KonfigDialog(self.konfig, [e.lstrip(".") for e in DS.speicherbare_endungen()], self)
        if dlg.exec() == QDialog.Accepted:
            self.konfig = dlg.ergebnis()
            KF.speichern(self.konfig)
            for a, c in self.art_boxen.items():
                if a != "gesamt":
                    c.setChecked(a in self.konfig.aktive_arten)

    def closeEvent(self, ev) -> None:
        if self.queue.laeuft:
            if QMessageBox.question(self, "Beenden", "Eine Prüfung läuft noch. Programm trotzdem beenden? Die Prüfung wird dabei abgebrochen.") != QMessageBox.Yes:
                ev.ignore()
                return
        self._ordner_offen.clear()
        if self._leser is not None:
            self._leser.wait(5000)
        self.queue.beenden_erzwingen()
        ev.accept()


def _temporaeres_aufraeumen() -> None:
    """Temporäre Prüfdaten (Bildzwischenspeicher, liegen gebliebene Arbeitsordner) entfernen. Dokumente und exportierte Ergebnisse liegen nie hier."""
    shutil.rmtree(KF.cacheordner(), ignore_errors=True)
    os.makedirs(KF.cacheordner(), exist_ok=True)
    jetzt = time.time()
    for p in glob.glob(os.path.join(tempfile.gettempdir(), "lunivo-pruefer-*")):
        try:
            if jetzt - os.stat(p).st_mtime > 600:                       # nur Reste älterer Läufe, nie die einer gerade laufenden Prüfung
                shutil.rmtree(p, ignore_errors=True)
        except OSError:
            pass


def starten(argv: list[str]) -> int:
    os.environ.setdefault("QT_LOGGING_RULES", "qt.qpa.fonts.warning=false")
    app = QApplication(argv)
    app.setApplicationName("Lunivo Writer")                  # gleiche Datenorte wie Lunivo; das Werkzeug legt darin nur seinen Unterordner an
    app.setOrganizationName("Lunivo")
    app.setStyle("Fusion")
    konfig = KF.laden()
    db = Datenbank(os.path.join(KF.datenordner(), "ergebnisse.sqlite"))
    db.sitzung_zuruecksetzen()                                    # jeder Start beginnt leer: keine Dateien, Ergebnisse, Läufe oder Fehler aus früheren Sitzungen
    _temporaeres_aufraeumen()
    fenster = Hauptfenster(db, konfig)

    def _unbehandelt(art, wert, tb) -> None:                      # ein Fehler in einer Funktion darf das Programm nicht beenden
        traceback.print_exception(art, wert, tb)
        try:
            fenster._zustand_setzen("fehler", f"Unerwarteter Fehler: {wert}. Das Programm läuft weiter; bei Wiederholung bitte „Neue Prüfung“ wählen.")
        except Exception:                                         # noqa: BLE001
            pass
    sys.excepthook = _unbehandelt
    fenster.show()
    code = app.exec()
    db.schliessen()
    return code


if __name__ == "__main__":
    sys.exit(starten(sys.argv))
