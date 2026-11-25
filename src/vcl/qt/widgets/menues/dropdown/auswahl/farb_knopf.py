"""Farb knopf: aus ``vcl.qt.widgets.menues.dropdown.auswahl.farbpalette`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter
from PySide6.QtWidgets import QToolButton
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import ICON_MITTEL
from vcl.qt.widgets.menues.dropdown.auswahl.farb_palette import FarbPalette


class FarbKnopf(QToolButton):
    """Geteilter Knopf fürs Band: Klick auf das Symbol wendet die letzte Farbe an, der Pfeil klappt die Palette auf."""

    angewendet = Signal(object)      # QColor oder None

    def __init__(self, symbol: QIcon | None = None, text: str = "", farbe: str | None = None, *, keine_text: str | None = "Keine Farbe",
                 titel: str = "Farbe", parent=None):
        super().__init__(parent)
        farbe = Farbe.ROT if farbe is None else farbe
        self._symbol, self.farbe, self._titel, self._keine = symbol, farbe, titel, keine_text
        self.setText(text); self.setToolTip(text or titel)
        self.setPopupMode(QToolButton.MenuButtonPopup)
        self.setToolButtonStyle(Qt.ToolButtonIconOnly if symbol else Qt.ToolButtonTextOnly)
        self.setIconSize(QSize(ICON_MITTEL, ICON_MITTEL))
        self.clicked.connect(lambda: self.angewendet.emit(QColor(self.farbe)))
        self.menu_neu()
        self._balken()

    def menu_neu(self) -> None:
        pal = FarbPalette(self, keine_text=self._keine, start=self.farbe, titel=self._titel)
        pal.gewaehlt.connect(self._gewaehlt)
        self.setMenu(pal)
        self._palette = pal

    def _gewaehlt(self, c: QColor | None) -> None:
        if c is not None:
            self.farbe = c.name(); self._balken()
        self.angewendet.emit(c)
        self.menu_neu()                                   # „Zuletzt benutzt“ aktualisieren

    def _balken(self) -> None:
        if self._symbol is None:
            return
        pm = self._symbol.pixmap(ICON_MITTEL, ICON_MITTEL)
        p = QPainter(pm); p.fillRect(2, pm.height() - 5, pm.width() - 4, 4, QColor(self.farbe)); p.end()
        self.setIcon(QIcon(pm))
