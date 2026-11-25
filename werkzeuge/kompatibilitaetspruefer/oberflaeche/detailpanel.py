"""Fehlerdetails zum gewählten Ergebnis: Kopfangaben, Prüfpunkte mit Referenz- und Lunivo-Wert, nicht geprüfte Eigenschaften."""
from __future__ import annotations

from kompatibilitaetspruefer.oberflaeche.layout import RasterSpalte
import json
from html import escape

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTextBrowser, QWidget

from kompatibilitaetspruefer.oberflaeche.modelle import FARBEN, REF_NAMEN
from kompatibilitaetspruefer.pruefung import klassifikation as K
from kompatibilitaetspruefer.oberflaeche.layout import FARBEN, HOEHE_DETAILPANEL_KOPF_MAX, HOEHE_DETAILPANEL_TEXT_MAX, stil


class DetailPanel(QWidget):
    vergleich = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.kopf = QTextBrowser()
        self.kopf.setOpenLinks(False)
        self.kopf.setMaximumHeight(HOEHE_DETAILPANEL_KOPF_MAX)
        self.tabelle = QTableWidget(0, 6)
        self.tabelle.setHorizontalHeaderLabels(["Prüfpunkt", "Ergebnis", "Fehlerart", "Schwere", "Referenz", "Lunivo"])
        self.tabelle.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabelle.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabelle.verticalHeader().setVisible(False)
        self.tabelle.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabelle.itemSelectionChanged.connect(self._zeile)
        self.text = QTextBrowser()
        self.knopf = QPushButton("Im Dokumentvergleich zeigen")
        self.knopf.clicked.connect(self.vergleich)
        self.knopf.setEnabled(False)
        lay = RasterSpalte(self)
        lay.addWidget(self.kopf)
        lay.addWidget(QLabel("Prüfpunkte"))
        lay.addWidget(self.tabelle, 1)
        lay.addWidget(self.text)
        lay.addWidget(self.knopf)
        self._befunde: list[dict] = []
        self.text.setMaximumHeight(HOEHE_DETAILPANEL_TEXT_MAX)

    def leeren(self) -> None:
        self.kopf.setHtml("<i>Kein Ergebnis ausgewählt.</i>")
        self.tabelle.setRowCount(0)
        self.text.clear()
        self.knopf.setEnabled(False)

    def zeige(self, zeile: dict, ergebnis: dict, befunde: list[dict], referenz: dict | None) -> None:
        werte = json.loads(ergebnis.get("werte_json") or "{}")
        bilder = json.loads(ergebnis.get("bilder_json") or "{}")
        ref = referenz or {}
        h = [f"<b>{escape(zeile['name'])}</b><br><small>{escape(zeile['pfad'])}</small><table cellspacing=2>"]
        for k, v in (("Dateiformat", zeile["endung"].lstrip(".").upper()), ("Ursprungsprogramm", zeile["programm"] or "unbekannt"),
                     ("Prüfart", K.PRUEFART_NAMEN.get(zeile["art"], zeile["art"])), ("Ergebnis", K.STATUS_NAMEN.get(zeile["status"], zeile["status"])),
                     ("Fehlerart", zeile["fehlerart"] or "–"), ("Schweregrad", zeile["schwere"]), ("Betroffene Seite", zeile["seite"] or "–"),
                     ("Betroffenes Element", zeile["element"] or "nicht bestimmbar"), ("Referenzstatus", REF_NAMEN.get(zeile["referenz"], zeile["referenz"])),
                     ("Referenz", (ref.get("programm", "") + " " + ref.get("programmversion", "") + " / " + ref.get("betriebssystem", "")).strip(" /") or "–"),
                     ("Prüfkonfiguration", ergebnis.get("konfig_hash", "")), ("Lunivo-Version", ergebnis.get("lunivo_version", ""))):
            farbe = FARBEN.get(zeile["status"] if k == "Ergebnis" else zeile["schwere"] if k == "Schweregrad" else "", "")
            stil = f' style="color:{farbe}"' if farbe else ""
            h.append(f"<tr><td><b>{k}</b></td><td{stil}>{escape(str(v))}</td></tr>")
        h.append(f"</table><p><b>Beschreibung:</b> {escape(zeile['beschreibung'] or '–')}</p>")
        self.kopf.setHtml("".join(h))
        self._befunde = befunde
        self.tabelle.setRowCount(len(befunde))
        for r, b in enumerate(befunde):
            for c, wert in enumerate((b["punkt"], K.PUNKT_NAMEN.get(b["status"], b["status"]), b["fehlerart"], b["schwere"], b["soll"], b["ist"])):
                item = QTableWidgetItem("" if wert in (None, "None") else str(wert))
                item.setToolTip(b["beschreibung"])
                if c == 3 and wert in FARBEN:
                    item.setForeground(self._farbe(wert))
                self.tabelle.setItem(r, c, item)
        nicht = werte.get("nicht_geprueft") or []
        zusatz = [f"<b>Nicht geprüft:</b> {escape('; '.join(nicht))}"] if nicht else []
        if werte.get("hinweis"):
            zusatz.append(f"<b>Hinweis:</b> {escape(werte['hinweis'])}")
        if werte.get("fehlende_schriften"):
            zusatz.append(f"<b>Nicht installierte Schriften:</b> {escape(', '.join(werte['fehlende_schriften']))}")
        self.text.setHtml("<br>".join(zusatz) or "<i>Keine weiteren Angaben.</i>")
        self.knopf.setEnabled(bool(bilder.get("lunivo")))
        self.tabelle.resizeColumnsToContents()
        self.tabelle.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    @staticmethod
    def _farbe(name: str):
        from PySide6.QtGui import QColor
        return QColor(FARBEN[name])

    def _zeile(self) -> None:
        r = self.tabelle.currentRow()
        if 0 <= r < len(self._befunde):
            b = self._befunde[r]
            zusatz = ""
            if b.get("seite"):
                zusatz += f"<br>Seite {b['seite']}"
            if b.get("element"):
                zusatz += f"<br>Element: {escape(b['element'])}"
            self.text.setHtml(f"<b>{escape(b['punkt'])}</b>: {escape(b['beschreibung'])}{zusatz}")
