"""Lesehilfe: Papierton, Abstände, Zeilenfokus und Absatzfokus — wirkt nur auf die Anzeige, nicht auf das gespeicherte Dokument.

Das Fenster klappt unter dem Knopf „Lesehilfe“ auf (Titel, Erklärung, sieben Felder, „Abbrechen“ und „Übernehmen“). Die Auswahlen kommen aus
``ui/lesestufen.py`` und sind dieselben wie in den Optionen ▸ Lesehilfe; geschrieben wird in dieselben Einstellungen."""
from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QComboBox, QDialog, QLabel, QVBoxLayout, QWidget

from lunivo_writer.ui import lesestufen as LS
from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.formular_gitter import FormularGitter
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig, leiste_fuer

from lunivo_writer.core.farben import Farbe
PAPIERTOENE = {"Weiß": Farbe.WEISS, "Creme": "#fbf4e2", "Gelblich": "#fff7cc", "Hellblau": "#e6f0fa",
               "Hellgrün": "#e8f5e9", "Hellgrau": "#eceff1"}
VORGABEN = {"papier": "Weiß", "buchstaben": 0.0, "wort": 0.0, "zeilenluft": 1.0, "zeilenfokus": False, "groesser": "keine", "zurueck": "keine"}


class LesehilfeDialog(PanelFaehig, QDialog):
    def __init__(self, fenster):
        super().__init__(fenster)
        self.setWindowTitle("Lesehilfe")
        self.w = fenster
        s = fenster.settings
        self._alt = {k: (s.get_bool("lesehilfe/" + k, False) if isinstance(v, bool) else s.get("lesehilfe/" + k, v)) for k, v in VORGABEN.items()}     # für „Abbrechen“
        v = QVBoxLayout(self)
        inhalt = QWidget(); form = FormularGitter(inhalt)
        er = QLabel("Erleichtert das Lesen am Bildschirm. Das Dokument bleibt, wie es ist — auf dem Papier steht nachher nichts davon.")
        er.setWordWrap(True); er.setStyleSheet("color: palette(mid);")
        form.breit(er)
        self.felder: dict[str, QComboBox] = {}

        def feld(schluessel: str, text: str, eintraege, standard) -> QComboBox:
            c = QComboBox()
            for anzeige, wert in eintraege:
                c.addItem(anzeige, wert)
            akt = s.get("lesehilfe/" + schluessel, standard)
            if isinstance(standard, bool):
                akt = s.get_bool("lesehilfe/" + schluessel, standard)
            elif isinstance(standard, float):
                akt = float(akt)
            c.setCurrentIndex(max(0, c.findData(akt)))
            c.currentIndexChanged.connect(lambda *_: self.anwenden())
            self.felder[schluessel] = c
            form.zeile(text, c)
            return c
        feld("papier", "Papierton", [(n, n) for n in PAPIERTOENE], "Weiß")
        feld("buchstaben", "Buchstabenabstand", LS.BUCHSTABEN, 0.0)
        feld("wort", "Wortabstand", LS.WORT, 0.0)
        feld("zeilenluft", "Zeilenluft", LS.ZEILENLUFT, 1.0)
        feld("zeilenfokus", "Zeilenfokus", LS.ZEILENFOKUS, False)
        feld("groesser", "Absatz beim Schreiben", LS.GROESSER, "keine")
        feld("zurueck", "Übriger Text", LS.ZURUECK, "keine")
        v.addWidget(inhalt)
        fussleiste(self, v, ok_text="Übernehmen")

    def zeige(self, knopf) -> None:
        """In der Seitenleiste öffnen (Standard); ohne Seitenleiste unter dem Knopf aufklappen."""
        if leiste_fuer(self) is not None:
            self.exec()
        else:
            self.zeige_unter(knopf)

    def zeige_unter(self, knopf) -> None:
        """Unter dem Knopf „Lesehilfe“ aufklappen (ohne ihn: wie ein gewöhnliches Fenster)."""
        self.setMinimumWidth(520)
        self.adjustSize()
        if knopf is not None:
            self.move(knopf.mapToGlobal(QPoint(0, knopf.height() + 4)))
        self.show()

    def anwenden(self) -> None:
        s = self.w.settings
        for k, c in self.felder.items():
            s.set("lesehilfe/" + k, c.currentData())
        self.w.lesehilfe_anwenden()

    def reject(self) -> None:
        """„Abbrechen“ stellt den Stand von vorher wieder her."""
        s = self.w.settings
        for k, wert in self._alt.items():
            s.set("lesehilfe/" + k, wert)
        self.w.lesehilfe_anwenden()
        super().reject()
