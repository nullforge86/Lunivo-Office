"""Reiter „Kompatibilitätsverbesserungen“: Entwicklungsübersicht über alle gespeicherten Prüfläufe und der Vorher-Nachher-Vergleich zweier Läufe (Verbesserungen, unveränderte Fehler,
Verschlechterungen, neue Fehler, nicht vergleichbare Paare). Alle Zahlen stammen aus gespeicherten Prüfläufen; es werden keine Quoten geschätzt."""
from __future__ import annotations

from kompatibilitaetspruefer.oberflaeche.layout import RasterSpalte, RasterZeile
import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QComboBox, QGroupBox, QHeaderView, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, QWidget

from kompatibilitaetspruefer.pruefung.klassifikation import PRUEFART_NAMEN, STATUS_NAMEN
from kompatibilitaetspruefer.verwaltung.fehlerverlauf import KLASSEN_NAMEN, format_von
from kompatibilitaetspruefer.oberflaeche.layout import FARBE_NEUTRAL, Kachelzeile, KLASSEN_FARBEN, SCHRIFT_PLUS_ERGEBNIS, STIL_HINWEIS, schrift_stufe, textzeile



def _zeit(z) -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(z)) if z else "–"


def _tabelle(spalten: tuple[str, ...]) -> QTableWidget:
    t = QTableWidget(0, len(spalten))
    t.setHorizontalHeaderLabels(list(spalten))
    t.setEditTriggers(QAbstractItemView.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectRows)
    t.verticalHeader().setVisible(False)
    t.setAlternatingRowColors(True)
    return t


def _zeilen_setzen(t: QTableWidget, zeilen: list[tuple], farbe_spalte: int = -1, farbe: str = "") -> None:
    t.setRowCount(len(zeilen))
    for r, z in enumerate(zeilen):
        for c, w in enumerate(z):
            it = QTableWidgetItem("" if w is None else str(w))
            it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if c == farbe_spalte and farbe:
                it.setForeground(QColor(farbe))
            t.setItem(r, c, it)
    t.resizeColumnsToContents()


class VerbesserungsPanel(QWidget):
    def __init__(self, verlauf, parent=None):
        super().__init__(parent)
        self.verlauf = verlauf
        self._erg: dict | None = None
        self.tabs = QTabWidget()

        # ---- Übersicht ----
        uebersicht = QWidget()
        raster = Kachelzeile()                                     # die Kennzahlen füllen die Breite und rücken bei schmalem Fenster in die nächste Zeile
        self.kennzahlen: dict[str, QLabel] = {}
        for i, (k, name, tip) in enumerate((("offen", "Offene Fehlergruppen", "Noch nicht als behoben bestätigt"),
                                            ("behoben", "Bestätigte Behebungen", "Durch eine erneute, vergleichbare Prüfung bestätigt"),
                                            ("weiter", "Weiterhin vorhanden", "Nach gemeldeter Korrektur bei erneuter Prüfung noch vorhanden"),
                                            ("neu", "Neu aufgetreten", "Erneut aufgetretene Gruppen plus neue Fehler im Vergleich der letzten beiden Läufe"),
                                            ("laeufe", "Gespeicherte Prüfläufe", "Jede vollständig beendete Prüfung wird festgehalten"))):
            box = QGroupBox(name)
            box.setToolTip(tip)
            l = RasterSpalte(box)
            w = QLabel("0")
            schrift_stufe(w, SCHRIFT_PLUS_ERGEBNIS, fett=True)
            w.setAlignment(Qt.AlignCenter)
            l.addWidget(w)
            self.kennzahlen[k] = w
            raster.hinzu(box)
        self.leer_hinweis = textzeile("")
        self.leer_hinweis.setWordWrap(True)
        self.leer_hinweis.setStyleSheet(STIL_HINWEIS)
        self.t_laeufe = _tabelle(("Lauf", "Zeitpunkt", "Lunivo-Kennung", "Dokumente", "Bestanden", "Auffällig", "Fehlgeschlagen", "Andere"))
        self.t_formate = _tabelle(("Lauf", "Format", "Dokumente", "Bestanden", "Auffällig", "Fehlgeschlagen", "Andere"))
        ul = RasterSpalte(uebersicht)
        ul.addWidget(raster)
        ul.addWidget(self.leer_hinweis)
        ul.addWidget(textzeile("<b>Entwicklung über die Prüfläufe</b> (Ergebnis je Dokument, ungünstigste Prüfart zählt)"))
        ul.addWidget(self.t_laeufe, 1)
        ul.addWidget(textzeile("<b>Entwicklung nach Dateiformat</b>"))
        ul.addWidget(self.t_formate, 1)
        self.tabs.addTab(uebersicht, "Übersicht")

        # ---- Vorher/Nachher ----
        vergleich = QWidget()
        self.alt, self.neu = QComboBox(), QComboBox()
        self.klasse = QComboBox()
        self.klasse.addItem("Alle Bewertungen", "")
        for k, n in KLASSEN_NAMEN.items():
            self.klasse.addItem(n, k)
        los = QPushButton("Vergleichen")
        los.clicked.connect(lambda *_: self.vergleichen())
        kopf = RasterZeile()
        kopf.addWidget(QLabel("Vorher:"))
        kopf.addWidget(self.alt, 1)
        kopf.addWidget(QLabel("Nachher:"))
        kopf.addWidget(self.neu, 1)
        kopf.addWidget(los)
        self.zusammenfassung = textzeile("Wählen Sie zwei Prüfläufe. Vergleichbar sind nur Paare mit gleichem Dokument, gleicher Referenz und gleicher Prüfkonfiguration.")
        self.zusammenfassung.setWordWrap(True)
        self.hinweise = textzeile("")
        self.hinweise.setWordWrap(True)
        self.hinweise.setStyleSheet(STIL_HINWEIS)
        self.t_vergleich = _tabelle(("Dokument", "Format", "Prüfart", "Vorher", "Nachher", "Bewertung", "Begründung", "Fehlergruppen"))
        self.klasse.currentIndexChanged.connect(lambda *_: self._anzeigen())
        vl = RasterSpalte(vergleich)
        vl.addLayout(kopf)
        vl.addWidget(self.zusammenfassung)
        vl.addWidget(self.hinweise)
        vl.addWidget(self.klasse)
        vl.addWidget(self.t_vergleich, 1)
        self.tabs.addTab(vergleich, "Vorher / Nachher")

        lay = RasterSpalte(self)
        lay.addWidget(self.tabs)

    # ---- Übersicht -------------------------------------------------------------------------------------------------
    def aktualisieren(self) -> None:
        u = self.verlauf.uebersicht()
        g = u["gruppen"]
        v = u["letzter_vergleich"] or {}
        self.kennzahlen["offen"].setText(str(g["offen"]))
        self.kennzahlen["behoben"].setText(str(g["behoben"]))
        self.kennzahlen["weiter"].setText(str(g["weiter"]))
        self.kennzahlen["neu"].setText(str(g["erneut"] + v.get("neu", 0)))
        self.kennzahlen["laeufe"].setText(str(len(u["laeufe"])))
        self.leer_hinweis.setText("" if u["laeufe"] else "Noch keine gespeicherten Prüfläufe. Nach der ersten vollständig beendeten Prüfung erscheinen hier Zahlen.")
        _zeilen_setzen(self.t_laeufe, [(f"Lauf {l['id']}", _zeit(l["zeit"]), (l["version"] or "")[:10], l["dateien"], l["bestanden"], l["auffaellig"], l["fehlgeschlagen"], l["andere"])
                                       for l in u["laeufe"]])
        zeilen = []
        for l in u["laeufe"]:
            for fmt, f in sorted(l["pro_format"].items()):
                zeilen.append((f"Lauf {l['id']}", fmt.upper(), f["gesamt"], f["bestanden"], f["auffaellig"], f["fehlgeschlagen"], f["andere"]))
        _zeilen_setzen(self.t_formate, zeilen)
        self._laeufe_combos()

    def _laeufe_combos(self) -> None:
        laeufe = self.verlauf.laeufe()
        alt_alt, neu_alt = self.alt.currentData(), self.neu.currentData()
        for c in (self.alt, self.neu):
            c.blockSignals(True)
            c.clear()
            for l in laeufe:
                c.addItem(f"Lauf {l['id']} — {_zeit(l['zeit'])} — Kennung {(l['lunivo_version'] or '')[:8]}", l["id"])
        i_neu = self.neu.findData(neu_alt)
        i_alt = self.alt.findData(alt_alt)
        self.neu.setCurrentIndex(i_neu if i_neu >= 0 else 0)
        self.alt.setCurrentIndex(i_alt if i_alt >= 0 else (1 if len(laeufe) > 1 else 0))
        for c in (self.alt, self.neu):
            c.blockSignals(False)

    # ---- Vorher/Nachher ------------------------------------------------------------------------------------------------
    def zeige_letzten_vergleich(self) -> None:
        """Nach einer erneuten Prüfung: die beiden neuesten Läufe vergleichen und den Vergleich zeigen."""
        self.aktualisieren()
        if self.neu.count() >= 2:
            self.neu.setCurrentIndex(0)
            self.alt.setCurrentIndex(1)
            self.vergleichen()
        self.tabs.setCurrentIndex(1)

    def vergleichen(self) -> None:
        a, n = self.alt.currentData(), self.neu.currentData()
        if a is None or n is None:
            self.zusammenfassung.setText("Es sind noch keine Prüfläufe gespeichert.")
            return
        if a == n:
            self.zusammenfassung.setText("Bitte zwei verschiedene Prüfläufe wählen.")
            return
        self._erg = self.verlauf.vergleiche_laeufe(a, n)
        z = self._erg["zaehler"]
        self.zusammenfassung.setText(" · ".join(f"{KLASSEN_NAMEN[k]}: {z[k]}" for k in KLASSEN_NAMEN))
        self.hinweise.setText(" ".join(self._erg["hinweise"]))
        self._anzeigen()

    def _anzeigen(self) -> None:
        if self._erg is None:
            return
        k = self.klasse.currentData()
        zeilen = [(e["name"], format_von(e["endung"]).upper(), PRUEFART_NAMEN.get(e["art"], e["art"]), STATUS_NAMEN.get(e["alt_status"], e["alt_status"] or "–"),
                   STATUS_NAMEN.get(e["neu_status"], e["neu_status"] or "–"), KLASSEN_NAMEN[e["klasse"]], e["grund"], ", ".join(e["gruppen"]))
                  for e in self._erg["eintraege"] if not k or e["klasse"] == k]
        _zeilen_setzen(self.t_vergleich, zeilen)
        for r, e in enumerate([e for e in self._erg["eintraege"] if not k or e["klasse"] == k]):
            it = self.t_vergleich.item(r, 5)
            if it is not None:
                it.setForeground(QColor(KLASSEN_FARBEN.get(e["klasse"], FARBE_NEUTRAL)))
