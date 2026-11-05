"""Auswahl von Voreinstellungen als Popup mit Bildchen in Abschnitten (Schatten: Kein, Außen, Innen, Perspektive; Leuchten; Spiegelung;
Material; Linien …).

    m = VoreinstellungMenue(parent, keine=("Kein Schatten", icon_oder_None))
    m.abschnitt("Außen", [("aussen1", icon, "Unten rechts"), …], spalten=3)
    m.gewaehlt.connect(lambda schluessel: …)         # "" = die Kein-Zeile
    m.exec(position)

Das Popup merkt nichts: es meldet nur den Schlüssel des gewählten Bildchens; wer es aufruft, setzt den Wert.
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QMenu, QToolButton, QVBoxLayout, QWidget, QWidgetAction
from lunivo_writer.ui.baukasten.karten_raster import kachel_gitter
from lunivo_writer.ui.baukasten.mass import (
    ABSTAND_KLEIN,
    ABSTAND_ZEILE,
    GROESSE_VORGABEMENUE_KACHEL,
    GROESSE_VORGABEMENUE_RAND,
    PADDING_VORGABEMENUE_KOPF,
    RADIUS_MARKE,
    RAND_KEIN,
    RAND_PANEL_KLEIN,
)
from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe


class VoreinstellungMenue(MenueListe):
    gewaehlt = Signal(str)

    def __init__(self, parent=None, *, keine: tuple[str, QIcon | None] | None = ("Keine", None), kachel: QSize = QSize(*GROESSE_VORGABEMENUE_KACHEL)):
        super().__init__(parent)
        self._kachel = kachel
        self._koerper = QWidget(); self._v = QVBoxLayout(self._koerper); self._v.setContentsMargins(*RAND_PANEL_KLEIN); self._v.setSpacing(ABSTAND_KLEIN)
        self.widget(self._koerper)
        self.aktuell: str | None = None
        if keine is not None:
            self._kopf(keine[0])
            if keine[1] is not None:
                self._gitter([("", keine[1], keine[0])], 1)

    def _kopf(self, text: str) -> None:
        l = QLabel(text); l.setStyleSheet("font-weight: 600; padding: " f"{PADDING_VORGABEMENUE_KOPF}" "; color: palette(text);")
        self._v.addWidget(l)

    def _gitter(self, eintraege: list[tuple[str, QIcon, str]], spalten: int) -> None:
        w = QWidget(); kacheln = []
        for i, (schl, icon, tipp) in enumerate(eintraege):
            k = QToolButton(); k.setAutoRaise(True); k.setIcon(icon); k.setIconSize(self._kachel); k.setToolTip(tipp)
            k.setFixedSize(self._kachel + QSize(*GROESSE_VORGABEMENUE_RAND)); k.setCheckable(True); k.setChecked(schl == self.aktuell)
            k.setStyleSheet("QToolButton { border: 1px solid transparent; border-radius: " f"{RADIUS_MARKE}" "px; }"
                            "QToolButton:hover { border-color: palette(highlight); } QToolButton:checked { border-color: palette(highlight); background: palette(midlight); }")
            k.clicked.connect(lambda _=False, s=schl: self._waehle(s))
            kacheln.append(k)
        kachel_gitter(kacheln, spalten, eltern=w, abstand=ABSTAND_ZEILE)
        self._v.addWidget(w)

    def abschnitt(self, titel: str, eintraege: list[tuple[str, QIcon, str]], spalten: int = 3) -> None:
        self._kopf(titel)
        self._gitter(eintraege, spalten)

    def _waehle(self, schluessel: str) -> None:
        self.gewaehlt.emit(schluessel)
        self.close()
