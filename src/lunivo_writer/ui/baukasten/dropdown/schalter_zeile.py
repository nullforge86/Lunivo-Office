"""Schalter-Zeile für Menüs: Symbol, Text und kleiner Kippschalter (``KippSchalter``). Ein Klick auf die ganze Zeile schaltet um; das Menü bleibt offen.
Gebaut aus ``MenueListe.schalter``; Maße aus ``mass.py``, Farben aus der Palette."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from lunivo_writer.ui.baukasten.basis.mass import ABSTAND_BLOCK, ABSTAND_MITTEL, DROPDOWN_ZEILE_PAD_V, ICON_NORMAL
from lunivo_writer.ui.baukasten.controls.schalter import KippSchalter


class SchalterZeile(QWidget):
    umgeschaltet = Signal(bool)

    def __init__(self, text: str, an: bool, symbol: QIcon | None = None, parent=None):
        super().__init__(parent)
        h = QHBoxLayout(self); h.setContentsMargins(ABSTAND_MITTEL, DROPDOWN_ZEILE_PAD_V, ABSTAND_MITTEL, DROPDOWN_ZEILE_PAD_V); h.setSpacing(ABSTAND_BLOCK)
        self.symbol = QLabel(); self.symbol.setFixedWidth(ICON_NORMAL)
        if symbol is not None:
            self.symbol.setPixmap(symbol.pixmap(ICON_NORMAL, ICON_NORMAL))
        h.addWidget(self.symbol)
        self.text = QLabel(text); h.addWidget(self.text, 1)
        self.schalter = KippSchalter(an)
        self.schalter.toggled.connect(self.umgeschaltet)
        h.addWidget(self.schalter)
        self.setCursor(Qt.PointingHandCursor)

    def an(self) -> bool:
        return self.schalter.isChecked()

    def an_setzen(self, an: bool) -> None:
        """Zustand von außen nachziehen, ohne ``umgeschaltet`` zu senden."""
        if an != self.schalter.isChecked():
            self.schalter.blockSignals(True); self.schalter.setChecked(an); self.schalter.blockSignals(False); self.schalter.update()

    def mousePressEvent(self, e) -> None:
        if e.button() == Qt.LeftButton and self.isEnabled():
            self.schalter.toggle()
        else:
            super().mousePressEvent(e)
