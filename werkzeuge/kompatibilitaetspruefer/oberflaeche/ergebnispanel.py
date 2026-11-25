"""Ergebnisübersicht: Kennzahlen, Aufschlüsselungen nach Format, Fehlerart und Schweregrad sowie die filterbare Ergebnisliste."""
from __future__ import annotations

from kompatibilitaetspruefer.oberflaeche.layout import RasterLayout, RasterSpalte, RasterZeile
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QCheckBox, QComboBox, QGroupBox, QHeaderView, QLabel, QLineEdit, QTableView, QTableWidget, QTableWidgetItem,
    QTabWidget, QWidget,
)

from kompatibilitaetspruefer.oberflaeche.modelle import FARBEN, FilterProxy, TabellenModell
from kompatibilitaetspruefer.pruefung import klassifikation as K
from kompatibilitaetspruefer.oberflaeche.layout import (
    FARBEN, HOEHE_AUFSCHLUESSELUNG_MAX, HOEHE_ZEILE_ERGEBNIS, SCHRIFT_PLUS_ERGEBNIS, schrift_stufe, stil_farbe,
)

STATUS_REIHE = (K.BESTANDEN, K.TEILWEISE, K.AUFFAELLIG, K.FEHLGESCHLAGEN, "nicht_pruefbar", K.ABGEBROCHEN)


class ErgebnisPanel(QWidget):
    gewaehlt = Signal(dict)           # Ergebniszeile
    vergleich_gewuenscht = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.kennzahlen: dict[str, QLabel] = {}
        raster = RasterLayout()
        for i, (schl, name) in enumerate((("alle", "Testdateien"), ("geprueft", "Geprüft"), ("bestanden", "Bestanden"), ("teilweise", "Teilweise geprüft"),
                                          ("auffaellig", "Auffällig"), ("fehlgeschlagen", "Fehlgeschlagen"), ("nicht_pruefbar", "Nicht prüfbar"), ("offen", "Offen"))):
            box = QGroupBox(name)
            l = RasterSpalte(box)
            wert = QLabel("0")
            schrift_stufe(wert, SCHRIFT_PLUS_ERGEBNIS, fett=True)
            wert.setAlignment(Qt.AlignCenter)
            if schl in FARBEN:
                wert.setStyleSheet(stil_farbe(FARBEN[schl]))
            l.addWidget(wert)
            self.kennzahlen[schl] = wert
            raster.addWidget(box, 0, i)
        self.prozent = QLabel("Fortschritt: 0 %")
        self.aufschluesselung = QTabWidget()
        self.t_format, self.t_art, self.t_schwere = QTableWidget(), QTableWidget(), QTableWidget()
        for t, name in ((self.t_format, "Nach Dateiformat"), (self.t_art, "Nach Fehlerart"), (self.t_schwere, "Nach Schweregrad")):
            t.setEditTriggers(QAbstractItemView.NoEditTriggers)
            t.verticalHeader().setVisible(False)
            self.aufschluesselung.addTab(t, name)
        self.aufschluesselung.setMaximumHeight(HOEHE_AUFSCHLUESSELUNG_MAX)
        self.modell = TabellenModell([("Dokument", "name"), ("Format", "format"), ("Prüfart", "art"), ("Ergebnis", "status"), ("Fehlerart", "fehlerart"),
                                      ("Schwere", "schwere"), ("Beschreibung", "beschreibung"), ("Referenz", "referenz"), ("Ursprung", "programm")])
        self.proxy = FilterProxy(self)
        self.proxy.setSourceModel(self.modell)
        self.suche = QLineEdit()
        self.suche.setPlaceholderText("Dateiname suchen …")
        self.suche.setClearButtonEnabled(True)
        self.suche.textChanged.connect(self._suche)
        self.f = {}
        zeile = RasterZeile()
        zeile.addWidget(self.suche, 2)
        for schl, name in (("endung", "Alle Formate"), ("status", "Alle Ergebnisse"), ("fehlerart", "Alle Fehlerarten"), ("schwere", "Alle Schweregrade"), ("programm", "Alle Programme")):
            c = QComboBox()
            c.addItem(name, "")
            c.currentIndexChanged.connect(self._filter)
            self.f[schl] = c
            zeile.addWidget(c, 1)
        for s in STATUS_REIHE:
            self.f["status"].addItem(K.STATUS_NAMEN.get(s, s), s)
        for a in K.FEHLERARTEN:
            self.f["fehlerart"].addItem(a, a)
        for s in K.SCHWEREN:
            self.f["schwere"].addItem(s, s)
        self.ohne_ref = QCheckBox("Nur fehlende/unsichere Referenz")
        self.ohne_ref.toggled.connect(self._ohne_ref)
        zeile.addWidget(self.ohne_ref)
        self.tabelle = QTableView()
        self.tabelle.setModel(self.proxy)
        self.tabelle.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabelle.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tabelle.setSortingEnabled(True)
        self.tabelle.setAlternatingRowColors(True)
        self.tabelle.verticalHeader().setVisible(False)
        self.tabelle.verticalHeader().setDefaultSectionSize(HOEHE_ZEILE_ERGEBNIS)
        self.tabelle.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.tabelle.selectionModel().selectionChanged.connect(self._auswahl)
        self.tabelle.doubleClicked.connect(lambda i: self.vergleich_gewuenscht.emit(self.proxy.data(i, Qt.UserRole)))
        self.anzahl = QLabel("")
        lay = RasterSpalte(self)
        lay.addLayout(raster)
        lay.addWidget(self.prozent)
        lay.addWidget(self.aufschluesselung)
        lay.addLayout(zeile)
        lay.addWidget(self.tabelle, 1)
        lay.addWidget(self.anzahl)

    def _suche(self, t: str) -> None:
        self.proxy.setze_suche(t)
        self._zaehl()

    def _filter(self) -> None:
        self.proxy.setze_filter(**{k: c.currentData() for k, c in self.f.items()})
        self._zaehl()

    def _ohne_ref(self, an: bool) -> None:
        self.proxy.nur_ohne_referenz = an
        self.proxy.invalidateFilter()
        self._zaehl()

    def _zaehl(self) -> None:
        self.anzahl.setText(f"{self.proxy.rowCount()} von {self.modell.rowCount()} Ergebnissen")

    def _auswahl(self, *_):
        zeilen = self.tabelle.selectionModel().selectedRows()
        if zeilen:
            self.gewaehlt.emit(self.proxy.data(zeilen[0], Qt.UserRole))

    def ausgewaehlt(self) -> dict | None:
        z = self.tabelle.selectionModel().selectedRows()
        return self.proxy.data(z[0], Qt.UserRole) if z else None

    def sichtbare_ergebnisse(self) -> list[dict]:
        return self.proxy.zeilen_sichtbar()

    # ---- Daten -----------------------------------------------------------------------------------------------------
    def setze(self, dateien: list[dict], dateistatus: dict[int, list[str]], zeilen: list[dict]) -> None:
        """Kennzahlen zählen **Dateien** (ungünstigster Status über alle ihre Prüfarten); die Aufschlüsselungen zählen **Ergebnisse** (Datei × Prüfart)."""
        for z in zeilen:
            z["format"] = z["endung"].lstrip(".").upper()
        gewaehlt = (self.ausgewaehlt() or {}).get("ergebnis_id")
        scroll = self.tabelle.verticalScrollBar().value()
        self.modell.setze(zeilen)
        self.proxy.sort(self.tabelle.horizontalHeader().sortIndicatorSection(), self.tabelle.horizontalHeader().sortIndicatorOrder())
        self._combo_nachfuellen("endung", sorted({z["endung"] for z in zeilen}), lambda e: e.lstrip(".").upper())
        self._combo_nachfuellen("programm", sorted({z["programm"] for z in zeilen if z["programm"]}), str)
        stati = {d["id"]: K.gesamt_status(dateistatus.get(d["id"], [])) for d in dateien}
        zaehler = {s: 0 for s in ("bestanden", "teilweise", "auffaellig", "fehlgeschlagen", "nicht_pruefbar", "abgebrochen", "offen")}
        for s in stati.values():
            zaehler[s] = zaehler.get(s, 0) + 1
        alle = len(dateien)
        offen = zaehler["offen"] + zaehler["abgebrochen"]
        geprueft = alle - offen
        for k, w in (("alle", alle), ("geprueft", geprueft), ("bestanden", zaehler["bestanden"]), ("teilweise", zaehler["teilweise"]), ("auffaellig", zaehler["auffaellig"]),
                     ("fehlgeschlagen", zaehler["fehlgeschlagen"]), ("nicht_pruefbar", zaehler["nicht_pruefbar"]), ("offen", offen)):
            self.kennzahlen[k].setText(str(w))
        self.prozent.setText(f"Fortschritt: {100 * geprueft / alle:.0f} % ({geprueft} von {alle} Dateien mit Ergebnis) — „bestanden“ nur, wenn alle Prüfpunkte aller geprüften Arten übereinstimmen"
                             if alle else "Fortschritt: keine Dateien")
        self._tabelle_fuellen(self.t_format, "Format", sorted({z["format"] for z in zeilen}), lambda z, w: z["format"] == w, zeilen)
        self._tabelle_fuellen(self.t_art, "Fehlerart", [a for a in K.FEHLERARTEN if any(z["fehlerart"] == a for z in zeilen)], lambda z, w: z["fehlerart"] == w, zeilen)
        self._tabelle_fuellen(self.t_schwere, "Schweregrad", [s for s in K.SCHWEREN if any(z["schwere"] == s and z["status"] in (K.AUFFAELLIG, K.FEHLGESCHLAGEN) for z in zeilen)],
                              lambda z, w: z["schwere"] == w and z["status"] in (K.AUFFAELLIG, K.FEHLGESCHLAGEN), zeilen)
        self._zaehl()
        if gewaehlt is not None:
            self.tabelle.selectionModel().blockSignals(True)
            for r in range(self.proxy.rowCount()):
                if self.proxy.data(self.proxy.index(r, 0), Qt.UserRole)["ergebnis_id"] == gewaehlt:
                    self.tabelle.selectRow(r)
                    break
            self.tabelle.selectionModel().blockSignals(False)
        self.tabelle.verticalScrollBar().setValue(scroll)

    def _combo_nachfuellen(self, schl: str, werte: list, name) -> None:
        c = self.f[schl]
        aktuell = c.currentData()
        c.blockSignals(True)
        c.clear()
        c.addItem({"endung": "Alle Formate", "programm": "Alle Programme"}[schl], "")
        for w in werte:
            c.addItem(name(w), w)
        c.setCurrentIndex(max(0, c.findData(aktuell)))
        c.blockSignals(False)

    @staticmethod
    def _tabelle_fuellen(t: QTableWidget, kopf: str, schluessel: list, passt, zeilen: list[dict]) -> None:
        spalten = [kopf, "Ergebnisse"] + [K.STATUS_NAMEN[s] for s in STATUS_REIHE]
        t.clear()
        t.setColumnCount(len(spalten))
        t.setRowCount(len(schluessel))
        t.setHorizontalHeaderLabels(spalten)
        for r, w in enumerate(schluessel):
            gruppe = [z for z in zeilen if passt(z, w)]
            t.setItem(r, 0, QTableWidgetItem(str(w)))
            t.setItem(r, 1, QTableWidgetItem(str(len(gruppe))))
            for c, s in enumerate(STATUS_REIHE, start=2):
                t.setItem(r, c, QTableWidgetItem(str(sum(1 for z in gruppe if z["status"] == s))))
        t.resizeColumnsToContents()
