"""Dialog „Seriendruck“: Empfängerliste eingeben oder aus einer Datei laden."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QPlainTextEdit, QPushButton

from lunivo_writer.oberflaeche.baukasten.basis.beschriftung import text_label
from lunivo_writer.oberflaeche.baukasten.basis.mass import GROESSE_FENSTER_SENDUNG
from lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster import Dateifenster
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FlussLayout
from lunivo_writer.oberflaeche.baukasten.geruest.rollen import spalte as _spalte
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.funktionen.sendungen.dialoge.dialog_hilfen import ok_zeile


class SeriendruckDialog(PanelFaehig, QDialog):
    def __init__(self, parent, felder: list[str], gespeichert: str):
        super().__init__(parent)
        self.setWindowTitle("Seriendruck")
        self.resize(*GROESSE_FENSTER_SENDUNG)
        v = _spalte("standard", self)
        v.addWidget(text_label(                                                  # bricht um: in der Seitenleiste wird nichts abgeschnitten
            ("Im Text gefunden: " + ", ".join("{{" + x + "}}" for x in felder) + "\nDie erste Zeile unten muss diese Namen enthalten.")
            if felder else "Im Text stehen noch keine Platzhalter. Fügen Sie Felder über Sendungen ▸ Seriendruckfeld ein\n"
                           "(oder schreiben Sie {{Name}} in den Text) und kommen Sie dann hierher zurück."))
        self.daten = QPlainTextEdit(gespeichert or (";".join(felder) + "\n" if felder else "Name;Ort\nFrau Meier;Kiel\nHerr Schmidt;Bonn"))
        v.addWidget(self.daten)
        z = FlussLayout()
        b = QPushButton("Aus Datei laden (CSV/TXT) …"); b.clicked.connect(self._laden); z.addWidget(b)
        v.addLayout(z)
        v.addWidget(ok_zeile(self, "Briefe erzeugen"))

    def _laden(self):
        pfad, _ = Dateifenster.getOpenFileName(self, "Empfängerliste", "", "Tabellen (*.csv *.txt *.tsv);;Alle Dateien (*)")
        if pfad:
            for enc in ("utf-8-sig", "cp1252"):
                try:
                    self.daten.setPlainText(open(pfad, encoding=enc).read()); break
                except (UnicodeDecodeError, OSError):
                    continue
