"""Grafische Konfiguration: Speicherorte, Prüfarten, Exportformate, visuelle Toleranzen, Verarbeitungsgrenzen und Parallelität. Die Vorgaben sind in ``Konfiguration`` begründet."""
from __future__ import annotations

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (QCheckBox, QDialog, QDialogButtonBox, QDoubleSpinBox, QFileDialog, QFormLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QSpinBox, QVBoxLayout,
                               QWidget)

from kompatibilitaetspruefer.pruefung.klassifikation import PRUEFART_NAMEN
from kompatibilitaetspruefer.verwaltung.konfiguration import ALLE_ARTEN, Konfiguration


class KonfigDialog(QDialog):
    def __init__(self, k: Konfiguration, speicherformate: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Konfiguration")
        _a = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(min(560, int(_a.width() * 0.9)), min(640, int(_a.height() * 0.85)))
        self.k = k
        self.test, self.ref, self.erg = QLineEdit(k.testordner), QLineEdit(k.referenzordner), QLineEdit(k.ergebnisordner)
        orte = QFormLayout()
        for name, feld, tip in (("Testdateien", self.test, ""), ("Referenzdateien", self.ref, "Zusätzlicher Suchort für namensgleiche Referenz-PDFs"),
                                ("Ergebnisse (Exporte)", self.erg, "Leer: Datenordner des Werkzeugs")):
            orte.addRow(name, self._ordnerzeile(feld))
            feld.setToolTip(tip)
        self.unter = QCheckBox("Unterordner beim Einlesen einbeziehen")
        self.unter.setChecked(k.unterordner)
        g_orte = QGroupBox("Speicherorte")
        l = QVBoxLayout(g_orte)
        l.addLayout(orte)
        l.addWidget(self.unter)
        self.arten = {a: QCheckBox(PRUEFART_NAMEN[a]) for a in ALLE_ARTEN}
        g_arten = QGroupBox("Aktivierte Prüfarten (Vorauswahl)")
        l = QVBoxLayout(g_arten)
        for a, c in self.arten.items():
            c.setChecked(a in k.aktive_arten)
            l.addWidget(c)
        self.formate = {f: QCheckBox(f.upper()) for f in speicherformate}
        g_fmt = QGroupBox("Exportprüfung: Zielformate")
        h = QHBoxLayout(g_fmt)
        for f, c in self.formate.items():
            c.setChecked(f in k.exportformate)
            h.addWidget(c)
        self.roundtrip = QCheckBox("Roundtrip zusätzlich mit gezielter Bearbeitung (Marke einfügen, speichern, neu öffnen)")
        self.roundtrip.setChecked(k.roundtrip_bearbeitung)
        self.zell = self._dspin(k.zellanteil * 100, 1, 50, " %", "Ab diesem Tintenunterschied je Rasterzelle (2 mm) gilt die Zelle als abweichend; fängt Kantenglättung und Schrift-Rendering ab")
        self.seiten_anteil = self._dspin(k.seitenanteil * 100, 0, 50, " %", "Bis zu diesem Anteil abweichender Rasterzellen bleibt eine Seite „innerhalb der Toleranz“")
        self.versatz = self._dspin(k.verschiebung_mm, 0.5, 30, " mm", "Toleranz für verschobene Inhaltsbereiche und Seitenränder")
        g_tol = QGroupBox("Visuelle Vergleichstoleranzen")
        f = QFormLayout(g_tol)
        f.addRow("Zellabweichung", self.zell)
        f.addRow("Seitentoleranz", self.seiten_anteil)
        f.addRow("Verschiebung", self.versatz)
        self.zeit = self._spin(k.zeitlimit_s, 10, 7200, " s")
        self.speicher = self._spin(k.speicher_mb, 0, 262144, " MB")
        self.speicher.setSpecialValueText("keine Grenze")
        self.max_seiten = self._spin(k.max_seiten, 1, 2000, " Seiten")
        self.max_mb = self._spin(k.max_dateigroesse_mb, 1, 4096, " MB")
        self.parallel = self._spin(k.parallel, 1, 32, "")
        self.dpi = self._dspin(k.rendern_dpi_faktor, 0.5, 3.0, " ×", "1,0 = 96 dpi")
        g_gr = QGroupBox("Verarbeitungsgrenzen")
        f = QFormLayout(g_gr)
        f.addRow("Zeitlimit je Datei", self.zeit)
        f.addRow("Speichergrenze je Prüfprozess", self.speicher)
        f.addRow("Bildlich verglichene Seiten (max.)", self.max_seiten)
        f.addRow("Größte zulässige Datei", self.max_mb)
        f.addRow("Parallele Prüfprozesse", self.parallel)
        f.addRow("Darstellungsauflösung", self.dpi)
        tasten = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        tasten.accepted.connect(self.accept)
        tasten.rejected.connect(self.reject)
        lay = QVBoxLayout(self)
        for w in (g_orte, g_arten, g_fmt, self.roundtrip, g_tol, g_gr, tasten):
            lay.addWidget(w)

    @staticmethod
    def _spin(wert, lo, hi, suffix) -> QSpinBox:
        s = QSpinBox()
        s.setRange(lo, hi)
        s.setValue(int(wert))
        s.setSuffix(suffix)
        return s

    @staticmethod
    def _dspin(wert, lo, hi, suffix, tip="") -> QDoubleSpinBox:
        s = QDoubleSpinBox()
        s.setRange(lo, hi)
        s.setDecimals(1)
        s.setValue(float(wert))
        s.setSuffix(suffix)
        s.setToolTip(tip)
        return s

    def _ordnerzeile(self, feld: QLineEdit) -> QWidget:
        w = QWidget()
        h = QHBoxLayout(w)
        h.setContentsMargins(0, 0, 0, 0)
        b = QPushButton("…")
        b.setFixedWidth(32)
        b.clicked.connect(lambda: feld.setText(QFileDialog.getExistingDirectory(self, "Ordner wählen", feld.text()) or feld.text()))
        h.addWidget(feld, 1)
        h.addWidget(b)
        return w

    def ergebnis(self) -> Konfiguration:
        k = Konfiguration.aus_dict(self.k.als_dict())
        k.testordner, k.referenzordner, k.ergebnisordner = self.test.text().strip(), self.ref.text().strip(), self.erg.text().strip()
        k.unterordner = self.unter.isChecked()
        k.aktive_arten = [a for a, c in self.arten.items() if c.isChecked()]
        k.exportformate = [f for f, c in self.formate.items() if c.isChecked()]
        k.roundtrip_bearbeitung = self.roundtrip.isChecked()
        k.zellanteil, k.seitenanteil, k.verschiebung_mm = self.zell.value() / 100, self.seiten_anteil.value() / 100, self.versatz.value()
        k.zeitlimit_s, k.speicher_mb, k.max_seiten, k.max_dateigroesse_mb, k.parallel = (self.zeit.value(), self.speicher.value(), self.max_seiten.value(), self.max_mb.value(),
                                                                                      self.parallel.value())
        k.rendern_dpi_faktor = self.dpi.value()
        return k
