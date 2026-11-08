"""Das Rahmen-Menü (Unten, Oben, Links, Rechts, Kein, Alle, Außen, Innen): ein Dropdown-Baustein, erbt alles von ``MenueListe``."""
from __future__ import annotations

from PySide6.QtCore import Signal

from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
from lunivo_writer.ui.baukasten.basis.linien import RAHMEN_EINTRAEGE, rahmen_symbol


class RahmenMenue(MenueListe):
    """Das Rahmen-Menü (Unten, Oben, Links, Rechts, Kein, Alle, Außen, Innen). Meldet die gewählten Seiten."""

    gewaehlt = Signal(object, str)         # RahmenSeiten, Schlüssel ('unten', 'alle', 'kein' …)

    def __init__(self, parent=None, *, innen: bool | str = True, mehr_text: str | None = "Rahmen und Schattierung …", mehr=None):
        """``innen``: True = beide inneren Linien (Tabelle), ``"h"`` = nur die waagerechte (Absätze), False = keine."""
        super().__init__(parent)
        erlaubt = {True: "hv", False: ""}.get(innen, innen)
        for e in RAHMEN_EINTRAEGE:
            if e is None:
                self.trenner(); continue
            schl, text, seiten = e
            if schl.startswith("innen_") and schl[-1] not in erlaubt:
                continue
            self.eintrag(text, lambda s=seiten, k=schl: self.gewaehlt.emit(s, k), symbol=rahmen_symbol(seiten))
        if mehr_text and mehr is not None:
            self.trenner()
            self.eintrag(mehr_text, mehr)
