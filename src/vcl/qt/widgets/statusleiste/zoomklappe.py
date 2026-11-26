"""Zoom-Klappe der Statusleiste („Zoomfaktor“): feste Stufen, Seitenbreite, ganze Seite und ein Prozentfeld. Die Zeilen stehen Qt-frei in
``writer.funktionen.ansicht``; die Klappe meldet nur die Wahl."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QSpinBox, QWidget

from vcl.qt.widgets.menues.dropdown import MenueListe
from writer.funktionen.ansicht import ZOOM_PROZENT_MAX, ZOOM_PROZENT_MIN, ZOOMWAHLEN, Zoomwahl


class ZoomKlappe(MenueListe):
    prozent_gewaehlt = Signal(int)        # fester Wert oder Prozentfeld
    breite_gewaehlt = Signal()            # Seitenbreite
    text_gewaehlt = Signal()              # Textbreite
    seite_gewaehlt = Signal()             # ganze Seite

    def __init__(self, eltern: QWidget | None = None):
        super().__init__(eltern)
        self.eintrag("Zoomfaktor", aktiv=False)
        self._gruppe = QActionGroup(self)
        self._gruppe.setExclusionPolicy(QActionGroup.ExclusionPolicy.ExclusiveOptional)
        self._zeilen: list[tuple[Zoomwahl, QAction]] = []
        for wahl in ZOOMWAHLEN:
            a = self.eintrag(wahl.text, lambda wahl=wahl: self._waehlen(wahl), haken=False, gruppe=self._gruppe)
            self._zeilen.append((wahl, a))
        self.trenner()
        self.eintrag("Prozent:", aktiv=False)
        self.feld = QSpinBox()
        self.feld.setRange(ZOOM_PROZENT_MIN, ZOOM_PROZENT_MAX)
        self.feld.setSuffix(" %")
        self.feld.setKeyboardTracking(False)                         # beim Tippen erst der fertige Wert, nicht jede Ziffer
        self.feld.setAccessibleName("Zoom in Prozent")
        self.feld.valueChanged.connect(self.prozent_gewaehlt)
        self.widget(self.feld)

    def _waehlen(self, wahl: Zoomwahl) -> None:
        if wahl.art == "breite":
            self.breite_gewaehlt.emit()
        elif wahl.art == "text":
            self.text_gewaehlt.emit()
        elif wahl.art == "seite":
            self.seite_gewaehlt.emit()
        else:
            self.prozent_gewaehlt.emit(wahl.prozent)

    def zeigen(self, prozent: int) -> None:
        """Zeigt den geltenden Zoom: Haken an der passenden festen Stufe, Wert im Prozentfeld – ohne eine Wahl zu melden."""
        for wahl, a in self._zeilen:
            a.setChecked(wahl.art == "wert" and wahl.prozent == prozent)
        self.feld.blockSignals(True)
        self.feld.setValue(prozent)
        self.feld.blockSignals(False)
