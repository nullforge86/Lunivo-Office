"""Reiter „Fehlerbericht“: Fehlergruppen ansehen, auswählen, priorisieren, als Bericht/Arbeitsauftrag/Paket für die Entwickler-KI aufbereiten, Bearbeitungsstatus und Korrekturmeldungen
verwalten und eine ausdrücklich bestätigte erneute Prüfung anstoßen.

Nichts wird automatisch übertragen: Der Arbeitsauftrag geht nur in die Zwischenablage, das Paket nur in eine vom Benutzer gewählte Datei. Vor jedem Export zeigt ein Dialog,
welche Daten enthalten sind."""
from __future__ import annotations

import json
import os
import time
from html import escape as esc

from PySide6.QtCore import QItemSelectionModel, Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication
from PySide6.QtWidgets import (QAbstractItemView, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QHBoxLayout, QHeaderView, QInputDialog, QLabel,
                               QLineEdit, QMenu, QMessageBox, QPlainTextEdit, QPushButton, QSplitter, QTableWidget, QTableWidgetItem, QTabWidget, QTextBrowser, QToolButton, QVBoxLayout, QWidget)

from kompatibilitaetspruefer.oberflaeche.modelle import FARBEN, FlussLayout
from kompatibilitaetspruefer.pruefung.klassifikation import PRUEFART_NAMEN
from kompatibilitaetspruefer.verwaltung import entwicklerbericht as EB
from kompatibilitaetspruefer.verwaltung.fehlerverlauf import STATUS_NAMEN, URSACHE_NAMEN

SPALTEN = ("#", "Kennung", "Format", "Vermuteter Ursachenbereich", "Fehlerart", "Schwere", "Dokumente", "Bearbeitungsstatus", "Ursache")
MANUELLE_STATUS = ("neu", "vorgesehen", "bearbeitung", "pruefen", "nicht_reproduzierbar")      # „behoben“, „weiterhin vorhanden“ und „erneut aufgetreten“ setzt nur eine erneute Prüfung


def _zeit(z) -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(z)) if z else "–"


class OptionenDialog(QDialog):
    """Zeigt vor jedem Export, was enthalten ist, und lässt den Benutzer wählen, was darüber hinaus beigelegt wird."""

    def __init__(self, gruppen: list[dict], paket: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welche Daten werden übergeben?")
        z = EB.zaehlung(gruppen)
        info = QLabel(f"<b>{z['gruppen']} Fehlergruppen</b> mit <b>{z['dokumente']} betroffenen Dokumenten</b> werden aufbereitet.<br><br>"
                      "<b>Enthalten:</b> Kennung, Priorität und Schweregrad der Fehlergruppen · Fehlerart und Prüfpunkt · Dokumentbezeichnungen · Soll- und Istwerte sowie "
                      "Beschreibungen der Prüfpunkte · Prüfkonfiguration · Lunivo-Kennung<br>"
                      "<b>Nicht enthalten:</b> Dokumenttexte und Originaldokumente (außer Sie wählen es unten) · es erfolgt keine automatische Übertragung an eine KI oder einen Dienst")
        info.setWordWrap(True)
        info.setTextFormat(Qt.RichText)
        self.pfade = QComboBox()
        for k, n in EB.PFADMODI:
            self.pfade.addItem(n, k)
        self.bilder = QCheckBox("Vergleichsbilder (Seitenbilder) der ersten Dokumente je Fehlergruppe beilegen")
        self.originale = QCheckBox("Originaldokumente der betroffenen Dateien beilegen (können vertrauliche Inhalte enthalten)")
        self.bilder.setVisible(paket)
        self.originale.setVisible(paket)
        form = QFormLayout()
        form.addRow("Dokumentangaben:", self.pfade)
        tasten = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        tasten.button(QDialogButtonBox.Ok).setText("Weiter")
        tasten.button(QDialogButtonBox.Cancel).setText("Abbrechen")
        tasten.accepted.connect(self.accept)
        tasten.rejected.connect(self.reject)
        lay = QVBoxLayout(self)
        lay.addWidget(info)
        lay.addLayout(form)
        lay.addWidget(self.bilder)
        lay.addWidget(self.originale)
        lay.addWidget(tasten)
        self.setMinimumWidth(520)

    def optionen(self) -> dict:
        return {"pfade": self.pfade.currentData(), "bilder": self.bilder.isChecked(), "originale": self.originale.isChecked()}


class KorrekturDialog(QDialog):
    def __init__(self, anzahl: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Korrektur melden")
        self.beschreibung = QPlainTextEdit()
        self.beschreibung.setPlaceholderText("Was wurde laut Rückmeldung geändert? (Diese Angabe gilt als Meldung, nicht als Nachweis.)")
        self.module = QLineEdit()
        self.module.setPlaceholderText("Betroffene Module, z. B. lunivo_writer/adapter/… (falls bekannt)")
        tasten = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        tasten.accepted.connect(self.accept)
        tasten.rejected.connect(self.reject)
        lay = QVBoxLayout(self)
        lay.addWidget(QLabel(f"Korrektur für {anzahl} Fehlergruppe(n) melden. Die Gruppen gelten danach als „Korrektur gemeldet“ – behoben sind sie erst nach einer erneuten Prüfung."))
        lay.itemAt(0).widget().setWordWrap(True)
        lay.addWidget(self.beschreibung)
        lay.addWidget(self.module)
        lay.addWidget(tasten)
        self.resize(520, 300)


class FehlerPanel(QWidget):
    meldung = Signal(str)             # kurze Rückmeldung für die Statusleiste
    erneut_pruefen = Signal(dict)     # {"dokumente": {pfad: {"arten": [...], "referenz": {...}}}, "schluessel": [...]}
    geaendert = Signal()              # Status oder Korrekturen haben sich geändert

    def __init__(self, verlauf, db, konfig_fn, version_fn, ordner_fn, parent=None):
        super().__init__(parent)
        self.verlauf, self.db, self.konfig_fn, self.version_fn, self.ordner_fn = verlauf, db, konfig_fn, version_fn, ordner_fn
        self._gruppen: list[dict] = []
        self._kontext_: dict | None = None
        self._fuellt = False
        self._optionen = {"pfade": "name", "bilder": False, "originale": False}

        self.quelle = QComboBox()
        self.quelle.addItem("Aktuelle Prüfung", "sitzung")
        self.quelle.addItem("Gespeicherter Prüflauf", "verlauf")
        self.lauf = QComboBox()
        self.lauf.setVisible(False)
        self.modus = QComboBox()
        for k, n in EB.AUSWAHL_MODI:
            self.modus.addItem(n, k)
        self.zaehler = QLabel("Auswahl: 0 Fehlergruppen · 0 Dokumente")
        kopf = QVBoxLayout()
        kopf_a, kopf_b = QHBoxLayout(), QHBoxLayout()
        kopf_a.addWidget(QLabel("Datenquelle:"))
        kopf_a.addWidget(self.quelle)
        kopf_a.addWidget(self.lauf, 1)
        kopf_a.addStretch(1)
        kopf_b.addWidget(QLabel("Übergeben:"))
        kopf_b.addWidget(self.modus)
        kopf_b.addWidget(self.zaehler, 1)
        kopf.addLayout(kopf_a)
        kopf.addLayout(kopf_b)

        self.hinweis = QLabel("Noch keine Prüfergebnisse. Starten Sie zuerst eine Prüfung; danach erscheinen hier die Fehlergruppen.")
        self.hinweis.setWordWrap(True)
        self.hinweis.setStyleSheet("color: gray")
        self.tabelle = QTableWidget(0, len(SPALTEN))
        self.tabelle.setHorizontalHeaderLabels(list(SPALTEN))
        self.tabelle.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabelle.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabelle.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tabelle.verticalHeader().setVisible(False)
        self.tabelle.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabelle.setAlternatingRowColors(True)
        self.tabelle.setToolTip("Sortiert nach Priorität. Mehrere Zeilen mit Strg/Umschalt wählbar (für „Nur ausgewählte Fehlergruppen“).")
        self.detail = QTextBrowser()
        self.vorschau = QPlainTextEdit()
        self.vorschau.setReadOnly(True)
        self.vorschau.setPlaceholderText("Hier erscheint der Arbeitsauftrag, sobald Sie „Fehlerbericht für Entwickler-KI erstellen“ wählen.")
        self.unten = QTabWidget()
        self.unten.addTab(self.detail, "Einzelheiten der Fehlergruppe")
        self.unten.addTab(self.vorschau, "Arbeitsauftrag (Vorschau)")
        teiler = QSplitter(Qt.Vertical)
        teiler.addWidget(self.tabelle)
        teiler.addWidget(self.unten)
        teiler.setStretchFactor(0, 3)
        teiler.setStretchFactor(1, 2)

        def knopf(text: str, tip: str, fn, haupt: bool = False) -> QPushButton:
            b = QPushButton(text)
            b.setToolTip(tip)
            b.clicked.connect(lambda *_: fn())
            if haupt:
                b.setStyleSheet("font-weight: bold")
            return b
        zeile1 = FlussLayout(8)
        zeile1.addWidget(knopf("Fehlerbericht für Entwickler-KI erstellen", "Erstellt aus den gewählten Fehlergruppen den Bericht und den Arbeitsauftrag (Vorschau)", self.bericht_erstellen, True))
        zeile1.addWidget(knopf("KI-Arbeitsauftrag kopieren", "Kopiert den lesbaren Arbeitsauftrag in die Zwischenablage", self.auftrag_kopieren))
        zeile1.addWidget(knopf("Fehlerpaket exportieren …", "Schreibt Bericht und Arbeitsauftrag (optional Nachweise) in eine ZIP-Datei", self.paket_exportieren))
        self.mehr = QToolButton()
        self.mehr.setText("Weitere Aktionen ▾")
        self.mehr.setPopupMode(QToolButton.InstantPopup)
        menue = QMenu(self.mehr)
        for text, fn in (("Fehlergruppe anzeigen", self.gruppe_anzeigen), ("Bericht als JSON speichern …", self.json_speichern),
                         ("Ursache bestätigen …", self.ursache_bestaetigen), ("Korrektur melden …", self.korrektur_melden)):
            menue.addAction(text, fn)
        status_menue = menue.addMenu("Bearbeitungsstatus setzen auf")
        for s_ in MANUELLE_STATUS:
            status_menue.addAction(STATUS_NAMEN[s_], lambda s_=s_: self.status_setzen(s_))
        self.mehr.setMenu(menue)
        zeile1.addWidget(self.mehr)
        self.regression = QCheckBox("Auch zuvor bestandene Dokumente prüfen (Regressionsprüfung)")
        self.regression.setToolTip("Prüft zusätzlich alle Dokumente des Laufs erneut, um Verschlechterungen durch die Korrektur zu erkennen")
        zeile3 = QHBoxLayout()
        zeile3.addWidget(knopf("Nach Korrektur erneut prüfen", "Prüft die betroffenen Dokumente nach Ihrer Bestätigung erneut mit der aktuellen Lunivo-Implementierung", self.nach_korrektur_pruefen, True))
        zeile3.addWidget(self.regression)
        zeile3.addStretch(1)
        lay = QVBoxLayout(self)
        lay.addLayout(kopf)
        lay.addWidget(self.hinweis)
        lay.addWidget(teiler, 1)
        lay.addLayout(zeile1)
        lay.addLayout(zeile3)

        self.quelle.currentIndexChanged.connect(self._quelle_geaendert)
        self.lauf.currentIndexChanged.connect(lambda *_: self.neu_laden() if not self._fuellt else None)
        self.modus.currentIndexChanged.connect(lambda *_: self._zaehlen())
        self.tabelle.itemSelectionChanged.connect(self._auswahl_geaendert)

    # ---- Daten laden -----------------------------------------------------------------------------------------------
    def _quelle_geaendert(self) -> None:
        self.lauf.setVisible(self.quelle.currentData() == "verlauf")
        self.neu_laden()

    def _lauf_fuellen(self) -> None:
        aktuell = self.lauf.currentData()
        self._fuellt = True
        self.lauf.clear()
        for l in self.verlauf.laeufe():
            self.lauf.addItem(f"Lauf {l['id']} — {_zeit(l['zeit'])} — {l['anzahl_dateien']} Dokumente — Kennung {(l['lunivo_version'] or '')[:8]}", l["id"])
        i = self.lauf.findData(aktuell)
        self.lauf.setCurrentIndex(max(0, i))
        self._fuellt = False

    def _kontext(self) -> dict | None:
        if self.quelle.currentData() == "verlauf":
            lid = self.lauf.currentData()
            zeile = next((l for l in self.verlauf.laeufe() if l["id"] == lid), None)
            if zeile is None:
                return None
            try:
                konfig = json.loads(zeile["konfig_json"] or "{}")
            except ValueError:
                konfig = {}
            return {"datenquelle": f"Gespeicherter Prüflauf Nr. {lid} vom {_zeit(zeile['zeit'])}", "datensaetze": self.verlauf.datensaetze_verlauf(lid), "konfig": konfig,
                    "lunivo_version": zeile["lunivo_version"], "dateiliste": None, "zeit": zeile["zeit"]}
        daten = self.verlauf.datensaetze_live()
        refs = self.db.alle_referenzen()
        dateiliste = []
        for d in self.db.dateien():
            r = refs.get(d["id"])
            dateiliste.append({"name": d["name"], "pfad": d["pfad"], "endung": d["endung"],
                               "referenz": "visuell" if (r and (r.get("pdf") or r.get("bilder"))) else ("strukturell" if r else "keine")})
        zeiten = [d["zeit"] for d in daten if d.get("zeit")]
        return {"datenquelle": "Aktuelle Prüfung dieser Sitzung", "datensaetze": daten, "konfig": self.konfig_fn().als_dict(), "lunivo_version": self.version_fn(),
                "dateiliste": dateiliste, "zeit": max(zeiten) if zeiten else None}

    def neu_laden(self) -> None:
        gewaehlt = {g["gruppe_id"] for g in self._ausgewaehlte()}
        self._lauf_fuellen()
        self._kontext_ = self._kontext()
        self._gruppen = self.verlauf.gruppen_aus(self._kontext_["datensaetze"]) if self._kontext_ else []
        self._tabelle_fuellen(gewaehlt)
        if self._kontext_ is None or not self._kontext_["datensaetze"]:
            self.hinweis.setText("Noch keine Prüfergebnisse. Starten Sie zuerst eine Prüfung" if self.quelle.currentData() == "sitzung"
                                 else "Es ist noch kein Prüflauf gespeichert. Läufe werden nach jeder vollständig beendeten Prüfung automatisch festgehalten.")
        elif not self._gruppen:
            self.hinweis.setText("Keine Fehlergruppen: Alle geprüften Dokumente sind ohne Abweichung (Hinweise wie fehlende Referenz zählen nicht als Fehler).")
        else:
            self.hinweis.setText("Die Fehlergruppen sind nach Priorität sortiert. Der Ursachenbereich ist eine technische Vermutung, keine Diagnose.")
        self.detail.setHtml("")
        self._zaehlen()

    def _tabelle_fuellen(self, gewaehlt: set[str]) -> None:
        self._fuellt = True
        t = self.tabelle
        t.clearSelection()
        t.setRowCount(len(self._gruppen))
        for r, g in enumerate(self._gruppen):
            werte = (str(g["rang"]), g["gruppe_id"], g["format"].upper(), f"{g['bereich']} (vermutet)", g["fehlerart"], g["schwere"], str(g["anzahl"]),
                     STATUS_NAMEN.get(g["status"], g["status"]), URSACHE_NAMEN.get(g["ursache"], g["ursache"]))
            for c, w in enumerate(werte):
                it = QTableWidgetItem(w)
                it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if c == 5 and g["schwere"] in FARBEN:
                    it.setForeground(QColor(FARBEN[g["schwere"]]))
                t.setItem(r, c, it)
            if g["gruppe_id"] in gewaehlt:
                t.selectionModel().select(t.model().index(r, 0), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
        t.resizeColumnsToContents()
        t.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self._fuellt = False

    # ---- Auswahl --------------------------------------------------------------------------------------------------
    def _ausgewaehlte(self) -> list[dict]:
        zeilen = sorted({i.row() for i in self.tabelle.selectionModel().selectedRows()}) if self.tabelle.selectionModel() else []
        return [self._gruppen[r] for r in zeilen if 0 <= r < len(self._gruppen)]

    def _export_gruppen(self) -> list[dict]:
        return EB.auswahl_filtern(self._gruppen, self.modus.currentData(), {g["gruppe_id"] for g in self._ausgewaehlte()})

    def _auswahl_geaendert(self) -> None:
        if self._fuellt:
            return
        sel = self._ausgewaehlte()
        if len(sel) >= 1:
            self.detail.setHtml(self._detail_html(sel[0], False))
        self._zaehlen()

    def _zaehlen(self) -> None:
        z = EB.zaehlung(self._export_gruppen())
        self.zaehler.setText(f"Auswahl: {z['gruppen']} Fehlergruppen · {z['dokumente']} Dokumente")

    # ---- Darstellung ----------------------------------------------------------------------------------------------
    def _detail_html(self, g: dict, voll: bool) -> str:
        h = [f"<h3>{esc(g['gruppe_id'])} — {esc(g['fehlerart'])}</h3>"]
        h.append(f"<p><b>Format:</b> {esc(g['format'].upper())} · <b>Prüfart:</b> {esc(PRUEFART_NAMEN.get(g['art'], g['art']))} · <b>Prüfpunkt:</b> {esc(g['punkt'])} · "
                 f"<b>Schweregrad:</b> {esc(g['schwere'])} · <b>Bearbeitungsstatus:</b> {esc(STATUS_NAMEN.get(g['status'], g['status']))}</p>")
        h.append(f"<p><b>Beobachteter Fehler:</b> {esc(g['fehlerart'])} beim Prüfpunkt „{esc(g['punkt'])}“ in {g['anzahl']} Dokument(en).</p>")
        if g["ursache"] == "bestaetigt":
            h.append(f"<p><b>Bestätigte Ursache:</b> {esc(g['notiz'] or '(ohne Notiz)')} · Bereich: {esc(g['bereich'])}</p>")
        else:
            h.append(f"<p><b>Vermuteter Ursachenbereich:</b> {esc(g['bereich'])} <i>(nur vermutet, nicht bestätigt)</i></p>")
        h.append(f"<p><b>Priorität {g['prioritaet']} (Rang {g['rang']}) – so kommt sie zustande:</b></p><ul>" + "".join(f"<li>{esc(x)}</li>" for x in g["prioritaet_gruende"]) + "</ul>")
        r = g["referenzen"]
        h.append(f"<p><b>Vergleichsdaten:</b> {r.get('visuell', 0)} Dokumente mit Referenz-PDF/Seitenbildern, {r.get('strukturell', 0)} mit nur erwarteten Werten, {r.get('keine', 0)} ohne Referenz</p>")
        if g["seiten"]:
            h.append("<p><b>Beispielhafte Seiten:</b> " + ", ".join(str(s) for s in sorted(g["seiten"])[:10]) + "</p>")
        liste = g["dokumentliste"] if voll else g["dokumentliste"][:15]
        h.append(f"<p><b>Betroffene Dokumente ({g['anzahl']}):</b><br>" + "<br>".join(esc(d["name"]) + (f" <small>({esc(d['pfad'])})</small>" if voll else "") for d in liste)
                 + (f"<br>… und {g['anzahl'] - len(liste)} weitere" if len(liste) < g["anzahl"] else "") + "</p>")
        if g["beispiele"]:
            h.append("<p><b>Beobachtete Unterschiede (Beispiele):</b></p><ul>")
            for b in g["beispiele"][: (8 if voll else 4)]:
                teile = [esc(b["dokument"]) + (f", Seite {b['seite']}" if b["seite"] else "") + (f", {esc(b['element'])}" if b["element"] else "")]
                if b["soll"] or b["ist"]:
                    teile.append(f"Soll: {esc(b['soll'] or '–')} / Ist: {esc(b['ist'] or '–')}")
                if b["beschreibung"]:
                    teile.append(esc(b["beschreibung"][:300]))
                h.append("<li>" + " — ".join(teile) + "</li>")
            h.append("</ul>")
        if g["korrekturen"]:
            h.append("<p><b>Gemeldete Korrekturen (Meldungen, keine Nachweise):</b></p><ul>")
            for k in g["korrekturen"]:
                h.append(f"<li>{_zeit(k['zeit'])} — {esc(k['beschreibung'] or '(ohne Beschreibung)')} — Module: {esc(k['module'] or 'nicht angegeben')} — erneute Prüfung: {esc(k['pruefstatus'])}</li>")
            h.append("</ul>")
        return "".join(h)

    def gruppe_anzeigen(self) -> None:
        sel = self._ausgewaehlte()
        if not sel:
            self.meldung.emit("Bitte zuerst eine Fehlergruppe in der Liste wählen.")
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Fehlergruppe {sel[0]['gruppe_id']}")
        b = QTextBrowser()
        b.setHtml(self._detail_html(sel[0], True))
        lay = QVBoxLayout(dlg)
        lay.addWidget(b)
        tasten = QDialogButtonBox(QDialogButtonBox.Close)
        tasten.rejected.connect(dlg.reject)
        tasten.clicked.connect(lambda *_: dlg.accept())
        lay.addWidget(tasten)
        dlg.resize(760, 560)
        dlg.exec()

    # ---- Bericht, Arbeitsauftrag, Paket -------------------------------------------------------------------------------
    def _bauen(self, optionen: dict):
        gruppen = self._export_gruppen()
        if not gruppen or self._kontext_ is None:
            self.meldung.emit("Keine Fehlergruppen in der aktuellen Auswahl – es gibt nichts zu übergeben.")
            return None
        bericht, nachweise, originale = EB.bericht_erstellen(gruppen, self._kontext_, optionen)
        return gruppen, bericht, nachweise, originale, EB.arbeitsauftrag(bericht)

    def _abfragen(self, paket: bool) -> dict | None:
        gruppen = self._export_gruppen()
        if not gruppen:
            self.meldung.emit("Keine Fehlergruppen in der aktuellen Auswahl – es gibt nichts zu übergeben.")
            return None
        dlg = OptionenDialog(gruppen, paket, self)
        i = dlg.pfade.findData(self._optionen["pfade"])
        dlg.pfade.setCurrentIndex(max(0, i))
        if dlg.exec() != QDialog.Accepted:
            return None
        self._optionen = dlg.optionen()
        return dict(self._optionen)

    def _uebergeben(self, gruppen: list[dict]) -> None:
        """Neu erkannte, übergebene Gruppen gelten danach als „Zur Untersuchung vorgesehen“."""
        keys = [g["schluessel"] for g in gruppen if g["status"] == "neu"]
        if keys:
            self.verlauf.status_setzen(keys, "vorgesehen")
        self.neu_laden()
        self.geaendert.emit()

    def bericht_erstellen(self) -> None:
        erg = self._bauen({"pfade": self._optionen["pfade"], "bilder": False, "originale": False})
        if erg is None:
            return
        gruppen, bericht, _n, _o, text = erg
        self.vorschau.setPlainText(text)
        self.unten.setCurrentWidget(self.vorschau)
        self.meldung.emit(f"Fehlerbericht erstellt: {bericht['zusammenfassung']['gruppen']} Fehlergruppen, {bericht['zusammenfassung']['dokumente']} Dokumente. "
                          "Weiter mit „KI-Arbeitsauftrag kopieren“ oder „Fehlerpaket exportieren“.")

    def auftrag_kopieren(self) -> None:
        opt = self._abfragen(False)
        if opt is None:
            return
        erg = self._bauen({**opt, "bilder": False, "originale": False})
        if erg is None:
            return
        gruppen, _b, _n, _o, text = erg
        QGuiApplication.clipboard().setText(text)
        self.vorschau.setPlainText(text)
        self.meldung.emit(f"Arbeitsauftrag mit {len(gruppen)} Fehlergruppen in die Zwischenablage kopiert.")
        self._uebergeben(gruppen)

    def paket_exportieren(self) -> None:
        opt = self._abfragen(True)
        if opt is None:
            return
        erg = self._bauen(opt)
        if erg is None:
            return
        gruppen, bericht, nachweise, originale, text = erg
        start = os.path.join(self.ordner_fn(), "fehlerpaket_" + time.strftime("%Y%m%d-%H%M%S") + ".zip")
        pfad, _ = QFileDialog.getSaveFileName(self, "Fehlerpaket speichern", start, "ZIP (*.zip)")
        if not pfad:
            return
        try:
            n = EB.paket_schreiben(pfad, bericht, text, nachweise, originale)
        except (OSError, ValueError) as e:
            QMessageBox.warning(self, "Fehlerpaket", f"Das Paket konnte nicht geschrieben werden: {e}")
            return
        self.vorschau.setPlainText(text)
        self.meldung.emit(f"Fehlerpaket mit {len(gruppen)} Fehlergruppen ({n} Dateien) gespeichert: {pfad}")
        self._uebergeben(gruppen)

    def json_speichern(self) -> None:
        opt = self._abfragen(False)
        if opt is None:
            return
        erg = self._bauen({**opt, "bilder": False, "originale": False})
        if erg is None:
            return
        gruppen, bericht, _n, _o, text = erg
        start = os.path.join(self.ordner_fn(), "fehlerbericht_" + time.strftime("%Y%m%d-%H%M%S") + ".json")
        pfad, _ = QFileDialog.getSaveFileName(self, "Fehlerbericht speichern", start, "JSON (*.json)")
        if not pfad:
            return
        try:
            EB.json_schreiben(pfad, bericht)
        except (OSError, ValueError) as e:
            QMessageBox.warning(self, "Fehlerbericht", f"Der Bericht konnte nicht geschrieben werden: {e}")
            return
        self.vorschau.setPlainText(text)
        self.meldung.emit(f"Fehlerbericht ({len(gruppen)} Fehlergruppen) gespeichert: {pfad}")
        self._uebergeben(gruppen)

    # ---- Status, Ursache, Korrekturen -------------------------------------------------------------------------------------
    def _gewaehlt_oder_hinweis(self) -> list[dict] | None:
        sel = self._ausgewaehlte()
        if not sel:
            self.meldung.emit("Bitte zuerst eine oder mehrere Fehlergruppen in der Liste wählen.")
            return None
        return sel

    def status_setzen(self, status: str) -> None:
        sel = self._gewaehlt_oder_hinweis()
        if sel is None:
            return
        self.verlauf.status_setzen([g["schluessel"] for g in sel], status)
        self.meldung.emit(f"Status von {len(sel)} Fehlergruppe(n) auf „{STATUS_NAMEN[status]}“ gesetzt.")
        self.neu_laden()
        self.geaendert.emit()

    def ursache_bestaetigen(self) -> None:
        sel = self._gewaehlt_oder_hinweis()
        if sel is None:
            return
        text, ok = QInputDialog.getMultiLineText(self, "Ursache bestätigen", "Welche Ursache wurde nachgewiesen? (z. B. Modul und Funktion). Leer lassen und abbrechen, um die Vermutung zu behalten.")
        if ok and text.strip():
            self.verlauf.ursache_setzen([g["schluessel"] for g in sel], "bestaetigt", text.strip())
            self.meldung.emit("Ursache als bestätigt festgehalten.")
            self.neu_laden()
            self.geaendert.emit()

    def korrektur_melden(self) -> None:
        sel = self._gewaehlt_oder_hinweis()
        if sel is None:
            return
        dlg = KorrekturDialog(len(sel), self)
        if dlg.exec() != QDialog.Accepted:
            return
        self.verlauf.korrektur_melden([g["schluessel"] for g in sel], dlg.beschreibung.toPlainText().strip(), dlg.module.text().strip(), self.version_fn())
        self.meldung.emit(f"Korrektur für {len(sel)} Fehlergruppe(n) gemeldet. Zur Bestätigung: „Nach Korrektur erneut prüfen“.")
        self.neu_laden()
        self.geaendert.emit()

    # ---- Erneute Prüfung ------------------------------------------------------------------------------------------------
    def nach_korrektur_pruefen(self) -> None:
        if self._kontext_ is None:
            self.meldung.emit("Keine Daten für eine erneute Prüfung vorhanden.")
            return
        ziel = self._ausgewaehlte() or [g for g in self._gruppen if g["status"] in ("korrektur", "pruefen")]
        if not ziel:
            self.meldung.emit("Bitte Fehlergruppen wählen (oder zuerst eine Korrektur melden).")
            return
        referenz_von: dict[str, dict] = {}
        for r in self._kontext_["datensaetze"]:
            referenz_von.setdefault(r["pfad"], r.get("referenz_json") or {})
        dok: dict[str, dict] = {}
        for g in ziel:
            for d in g["dokumentliste"]:
                dok.setdefault(d["pfad"], {"arten": set(), "referenz": referenz_von.get(d["pfad"], {})})["arten"].add(g["art"])
        if self.regression.isChecked():
            for r in self._kontext_["datensaetze"]:
                if r["art"] != "darstellung":
                    dok.setdefault(r["pfad"], {"arten": set(), "referenz": referenz_von.get(r["pfad"], {})})["arten"].add(r["art"])
        vorhanden = sum(1 for p in dok if os.path.isfile(p))
        frage = (f"{len(dok)} Dokumente ({vorhanden} davon auffindbar) werden jetzt mit der aktuellen Lunivo-Implementierung erneut geprüft.\n\n"
                 "Die bisherigen Ergebnisse bleiben als früherer Prüflauf erhalten und werden anschließend verglichen. Jetzt starten?")
        if QMessageBox.question(self, "Nach Korrektur erneut prüfen", frage) != QMessageBox.Yes:
            return
        self.verlauf.status_setzen([g["schluessel"] for g in ziel if g["status"] in ("vorgesehen", "bearbeitung", "korrektur")], "pruefen")
        self.erneut_pruefen.emit({"dokumente": {p: {"arten": sorted(v["arten"]), "referenz": v["referenz"]} for p, v in dok.items()}, "schluessel": [g["schluessel"] for g in ziel]})
