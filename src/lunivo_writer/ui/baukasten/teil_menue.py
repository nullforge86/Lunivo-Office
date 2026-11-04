"""Der Pfeil am Hauptreiter („DIAGRAMM OPTIONEN ▾“): öffnet die Liste der Teile des Diagramms, der aktuelle Teil trägt einen Haken.

``setze(teile, aktuell)``: ``teile`` = Liste von (Schlüssel, Name); ``gewaehlt(schluessel)`` kommt bei der Wahl eines anderen Teils.
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import QToolButton

from lunivo_writer.ui.baukasten.menue_liste import MenueListe


class TeilMenueKnopf(QToolButton):
    gewaehlt = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._teile: list[tuple[str, str]] = []
        self._aktuell = ""
        self.setArrowType(Qt.DownArrow); self.setAutoRaise(True); self.setFocusPolicy(Qt.NoFocus)
        self.setFixedSize(36, 32); self.setToolTip("Diagrammteil wählen"); self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self._oeffnen)

    def setze(self, teile, aktuell: str) -> None:
        self._teile = [(str(k), str(n)) for k, n in teile]
        self._aktuell = aktuell

    def aktuell(self) -> str:
        return self._aktuell

    def _menue(self) -> MenueListe:
        m = MenueListe(self)
        for schl, name in self._teile:
            m.eintrag(name, lambda s=schl: self._waehlen(s), haken=schl == self._aktuell)
        return m

    def _waehlen(self, schluessel: str) -> None:
        if schluessel != self._aktuell:
            self._aktuell = schluessel
            self.gewaehlt.emit(schluessel)

    def _oeffnen(self) -> None:
        if not self._teile:
            return
        leiste = self.parentWidget() or self
        self._menue().exec(leiste.mapToGlobal(QPoint(0, leiste.height())))
