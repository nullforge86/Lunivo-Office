"""Auswahlliste mit Rahmen und hohen Zeilen — der eine Baustein für „Eintrag aus einer Liste wählen“ (Sprachen, Stimmen).

    liste = AuswahlListe([("de", "Deutsch"), ("en", "Englisch")])        # (Wert, Anzeigetext)
    liste.currentData()

Bedienbar wie eine Auswahl: ``currentData()``, ``currentText()``, ``setCurrentText()``, ``findData()``, ``setCurrentIndex()``.
Rahmen und Zeilenhöhe kommen aus dem Thema (``als_karte(…, "liste")``).
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from lunivo_writer.ui.baukasten.karte import als_karte
from lunivo_writer.ui.baukasten.mass import HOEHE_LISTE_REITER


class AuswahlListe(QListWidget):
    def __init__(self, eintraege: list[tuple[str, str]], mindesthoehe: int = HOEHE_LISTE_REITER):
        super().__init__()
        for daten, text in eintraege:
            it = QListWidgetItem(text); it.setData(Qt.UserRole, daten); self.addItem(it)
        als_karte(self, "liste")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumHeight(mindesthoehe)

    def currentData(self):
        it = self.currentItem()
        return it.data(Qt.UserRole) if it else None

    def currentText(self) -> str:
        it = self.currentItem()
        return it.text() if it else ""

    def findData(self, daten) -> int:
        return next((i for i in range(self.count()) if self.item(i).data(Qt.UserRole) == daten), -1)

    def setCurrentIndex(self, i: int) -> None:
        self.setCurrentRow(i)
        if 0 <= i < self.count():
            self.scrollToItem(self.item(i))

    def setCurrentText(self, text: str) -> None:
        self.setCurrentIndex(next((i for i in range(self.count()) if self.item(i).text() == text), -1))
