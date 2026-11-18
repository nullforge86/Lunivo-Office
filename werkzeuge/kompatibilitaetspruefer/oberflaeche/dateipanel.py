"""Verwaltung der Testdateien: Liste mit Suche, Filtern und Sortieren (Name, Format, Prüfstatus, Referenz)."""
from __future__ import annotations

from PySide6.QtCore import QItemSelectionModel, Qt, Signal
from PySide6.QtWidgets import (QAbstractItemView, QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QTableView, QToolButton, QVBoxLayout, QWidget)

from kompatibilitaetspruefer.oberflaeche.modelle import FORMAT_ZUSTAND, FilterProxy, TabellenModell
from kompatibilitaetspruefer.pruefung import klassifikation as K


class DateiPanel(QWidget):
    auswahl_geaendert = Signal(list)          # Datei-Ids
    hinzufuegen = Signal()
    ordner = Signal()
    entfernen = Signal()
    leeren = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.modell = TabellenModell([("Name", "name"), ("Format", "format"), ("Prüfstatus", "status"), ("Referenz", "referenz"), ("Ursprung", "programm")])
        self.proxy = FilterProxy(self)
        self.proxy.setSourceModel(self.modell)
        kopf = QHBoxLayout()
        for text, signal, tip in (("＋ Dateien", self.hinzufuegen, "Einzelne oder mehrere Dokumente hinzufügen"), ("📁 Ordner", self.ordner, "Ganzen Ordner einlesen"),
                                  ("− Entfernen", self.entfernen, "Ausgewählte aus der Prüfliste entfernen (Dateien bleiben unberührt)"),
                                  ("Liste leeren", self.leeren, "Prüfliste leeren (nach Bestätigung)")):
            b = QToolButton()
            b.setText(text)
            b.setToolTip(tip)
            b.clicked.connect(signal)
            kopf.addWidget(b)
        kopf.addStretch(1)
        self.zaehler = QLabel("0 Dateien")
        kopf.addWidget(self.zaehler)
        self.suche = QLineEdit()
        self.suche.setPlaceholderText("Dateiname suchen …")
        self.suche.setClearButtonEnabled(True)
        self.suche.textChanged.connect(self._suche)
        self.f_format, self.f_status, self.f_ref, self.f_prog = QComboBox(), QComboBox(), QComboBox(), QComboBox()
        self.f_format.addItem("Alle Formate", "")
        self.f_status.addItem("Alle Status", "")
        for s in ("offen", K.BESTANDEN, K.TEILWEISE, K.AUFFAELLIG, K.FEHLGESCHLAGEN, "nicht_pruefbar", K.ABGEBROCHEN):
            self.f_status.addItem(K.STATUS_NAMEN.get(s, s), s)
        self.f_ref.addItem("Alle Referenzen", "")
        for s, n in (("fehlt", "Referenz fehlt"), ("mehrdeutig", "mehrdeutig"), ("vorschlag", "Vorschlag offen"), ("zugeordnet", "zugeordnet"),
                     ("unvollstaendig", "nur erwartete Werte"), ("defekt", "Referenzdatei fehlt")):
            self.f_ref.addItem(n, s)
        self.f_prog.addItem("Alle Ursprungsprogramme", "")
        filter_zeile = QHBoxLayout()
        for c in (self.f_format, self.f_status, self.f_ref, self.f_prog):
            c.currentIndexChanged.connect(self._filter)
            filter_zeile.addWidget(c, 1)
        self.tabelle = QTableView()
        self.tabelle.setModel(self.proxy)
        self.tabelle.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabelle.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tabelle.setSortingEnabled(True)
        self.tabelle.verticalHeader().setVisible(False)
        self.tabelle.verticalHeader().setDefaultSectionSize(22)
        self.tabelle.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabelle.setAlternatingRowColors(True)
        self.tabelle.selectionModel().selectionChanged.connect(lambda *_: self.auswahl_geaendert.emit(self.ausgewaehlte_ids()))
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.addLayout(kopf)
        lay.addWidget(self.suche)
        lay.addLayout(filter_zeile)
        lay.addWidget(self.tabelle, 1)

    # ---- Daten -----------------------------------------------------------------------------------------------------
    def setze(self, dateien: list[dict], dateistatus: dict, referenz: dict) -> None:
        """``dateien`` aus der Datenbank; ``dateistatus``: Datei-Id → Statusliste; ``referenz``: Datei-Id → Anzeigezustand."""
        from kompatibilitaetspruefer.verwaltung.dateisuche import format_zustand
        zeilen = []
        formate, programme = set(), set()
        for d in dateien:
            zustand = format_zustand(d["endung"])
            formate.add(d["endung"])
            if d["programm"]:
                programme.add(d["programm"])
            zeilen.append({"id": d["id"], "name": d["name"], "pfad": d["pfad"], "endung": d["endung"], "format_zustand": zustand,
                           "format": (d["endung"].lstrip(".").upper() or "–") + FORMAT_ZUSTAND[zustand], "status": K.gesamt_status(dateistatus.get(d["id"], [])),
                           "referenz": referenz.get(d["id"], "fehlt"), "programm": d["programm"]})
        auswahl = self.ausgewaehlte_ids()
        self.modell.setze(zeilen)
        self._combo_fuellen(self.f_format, sorted(formate), "Alle Formate", lambda e: e.lstrip(".").upper())
        self._combo_fuellen(self.f_prog, sorted(programme), "Alle Ursprungsprogramme", str)
        self.proxy.sort(self.tabelle.horizontalHeader().sortIndicatorSection(), self.tabelle.horizontalHeader().sortIndicatorOrder())
        self._zaehler()
        if auswahl:
            self.waehle(auswahl)

    def _combo_fuellen(self, combo: QComboBox, werte: list, alle: str, name) -> None:
        aktuell = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(alle, "")
        for w in werte:
            combo.addItem(name(w), w)
        i = combo.findData(aktuell)
        combo.setCurrentIndex(max(0, i))
        combo.blockSignals(False)

    def _zaehler(self) -> None:
        self.zaehler.setText(f"{self.proxy.rowCount()} von {self.modell.rowCount()} Dateien")

    def _suche(self, text: str) -> None:
        self.proxy.setze_suche(text)
        self._zaehler()

    def _filter(self) -> None:
        self.proxy.setze_filter(endung=self.f_format.currentData(), status=self.f_status.currentData(), referenz=self.f_ref.currentData(), programm=self.f_prog.currentData())
        self._zaehler()

    def ausgewaehlte_ids(self) -> list[int]:
        return [self.proxy.data(i, Qt.UserRole)["id"] for i in self.tabelle.selectionModel().selectedRows()]

    def sichtbare_ids(self) -> list[int]:
        return [z["id"] for z in self.proxy.zeilen_sichtbar()]

    def alle_ids(self) -> list[int]:
        return [z["id"] for z in self.modell.zeilen]

    def zeilen_mit_id(self, ids: list[int]) -> list[dict]:
        wanted = set(ids)
        return [z for z in self.modell.zeilen if z["id"] in wanted]

    def waehle(self, ids: list[int]) -> None:
        wanted = set(ids)
        sm = self.tabelle.selectionModel()
        sm.blockSignals(True)
        sm.clearSelection()
        for r in range(self.proxy.rowCount()):
            if self.proxy.data(self.proxy.index(r, 0), Qt.UserRole)["id"] in wanted:
                sm.select(self.proxy.index(r, 0), QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows)
        sm.blockSignals(False)
