"""Symbolwahl: ein Knopf mit dem gewählten Symbol und Pfeil, der ein kleines Raster aus dem vorhandenen Symbolsystem aufklappt.

    wahl = SymbolWahl("assistent")                    # Wert = Schlüssel aus ``ui/widgets/icons``
    wahl.geaendert.connect(…); wahl.wert()

Öffnen, Lage und Größe des Aufklapprasters stammen aus dem Dropdown-Paket (``RasterAuswahl`` → ``MenueListe`` → ``PopupVerhalten``)."""
from __future__ import annotations

from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QIcon

from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownTaste
from lunivo_writer.ui.baukasten.dropdown.auswahl.raster_auswahl import RasterAuswahl
from lunivo_writer.ui.baukasten.basis.mass import GROESSE_SYMBOLWAHL, GROESSE_SYMBOLWAHL_KACHEL, ICON_NORMAL
from lunivo_writer.ui.widgets import icons

# (Schlüssel, Name) — Symbole des Katalogs, die zu Assistenten passen
ASSISTENT_SYMBOLE = (("ki", "KI"), ("assistent", "Assistent"), ("chat", "Chat"), ("sprechblase", "Sprechblase"), ("rechtschreibpruefung", "Rechtschreibung"),
                     ("zusammenfassen", "Zusammenfassen"), ("uebersetzen", "Übersetzen"), ("hervorheben", "Hervorheben"), ("lupe", "Prüfen"),
                     ("brille", "Lesen"), ("buch", "Buch"), ("stift", "Stift"), ("notiz", "Notiz"), ("zitat", "Zitat"), ("vorschlag", "Vorschlag"),
                     ("haken", "Haken"), ("thesaurus", "Wortschatz"), ("zahnrad", "Zahnrad"))
VORGABE_SYMBOL = "ki"


class SymbolAuswahl(RasterAuswahl):
    """Das Raster der Symbole (meldet den Schlüssel)."""

    def __init__(self, parent=None, symbole=ASSISTENT_SYMBOLE, aktuell: str = VORGABE_SYMBOL, spalten: int = 6):
        super().__init__(parent, spalten=spalten, groesse=QSize(*GROESSE_SYMBOLWAHL_KACHEL))
        for schl, name in symbole:
            self.kachel(schl, name, icons.icon(schl, ICON_NORMAL), aktuell=schl == aktuell)


class SymbolWahl(DropdownTaste):
    """Taste mit Symbol und Pfeil; ein Klick öffnet das Raster."""

    geaendert = Signal(str)

    def __init__(self, wert: str = VORGABE_SYMBOL, parent=None, symbole=ASSISTENT_SYMBOLE):
        super().__init__(parent)
        self._symbole = symbole
        self.setMinimumSize(*GROESSE_SYMBOLWAHL); self.setIconSize(QSize(ICON_NORMAL, ICON_NORMAL))
        self.setToolTip("Symbol wählen"); self.setAccessibleName("Symbol")
        self._wert = ""
        self.setzen(wert, melden=False)

    def wert(self) -> str:
        return self._wert

    def setzen(self, schluessel: str, melden: bool = True) -> None:
        if schluessel not in dict(self._symbole):
            schluessel = VORGABE_SYMBOL
        gleich = schluessel == self._wert
        self._wert = schluessel
        self.setIcon(icons.icon(schluessel, ICON_NORMAL))
        m = SymbolAuswahl(self, self._symbole, schluessel)
        m.gewaehlt.connect(self.setzen)
        self.menue_setzen(m, geteilt=False, besitzen=False)
        self._menue = m
        if melden and not gleich:
            self.geaendert.emit(schluessel)
