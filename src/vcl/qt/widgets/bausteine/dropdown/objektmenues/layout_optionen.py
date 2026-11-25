"""Das kleine Popup „Layoutoptionen“ neben einem markierten Bild: Umbruchart per Klick, „Mit Text verschieben“ oder „Fester Text“, „Mehr anzeigen“.

    p = LayoutOptionen(parent, art="hinter", mit_text=False)
    p.gewaehlt.connect(lambda art: ...); p.mehr.connect(...); p.verschieben.connect(lambda an: ...)
    p.zeigen_bei(globaler_punkt)

Das Popup ändert nichts selbst; es meldet nur, was gewählt wurde.
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.bausteine.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.bausteine.option.option import option

from vcl.qt.widgets.bausteine.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QFrame, QLabel, QPushButton, QRadioButton

from vcl.qt.widgets.bausteine.felder.kachel_feld import KachelFeld
from vcl.qt.widgets.bausteine.medien.umbruch_symbole import umbruch_zeichner
from writer.baukasten.basis.mass import ABSTAND_NORMAL, GROESSE_LAYOUTOPTIONEN_KACHEL, RAND_LAYOUTOPTIONEN
from vcl.qt.widgets.bausteine.dropdown.popup_lage import PopupVerhalten


class LayoutOptionen(PopupVerhalten, QFrame):
    gewaehlt = Signal(str)
    verschieben = Signal(bool)
    mehr = Signal()

    def __init__(self, parent=None, art: str = "textfluss", mit_text: bool = False):
        super().__init__(parent, Qt.Popup)
        self.setObjectName("layoutOptionen")
        self.setProperty("dropdownFenster", True)
        v = _spalte("panel", self)
        k = QLabel("Layoutoptionen"); k.setProperty("dropdownTitel", "kopf"); v.addWidget(k)
        v.addWidget(self._titel("Mit Text in Zeile"))
        self.zeile = KachelFeld(spalten=1, groesse=QSize(*GROESSE_LAYOUTOPTIONEN_KACHEL), mit_text=False)
        self.zeile.hinzu("textfluss", "Im Textfluss", umbruch_zeichner("textfluss"))
        v.addWidget(self.zeile)
        v.addWidget(self._titel("Zeilenumbruch"))
        self.umbruch = KachelFeld(spalten=3, groesse=QSize(*GROESSE_LAYOUTOPTIONEN_KACHEL), mit_text=False)
        for schl, text in (("quadrat", "Quadrat"), ("passend", "Passend"), ("transparent", "Transparent"), ("obenunten", "Oben und Unten"),
                           ("hinter", "Hinter den Text"), ("vor", "Vor dem Text")):
            self.umbruch.hinzu(schl, text, umbruch_zeichner(schl))
        v.addWidget(self.umbruch)
        for f in (self.zeile, self.umbruch):
            f.gewaehlt.connect(self._klick)
        self.r_mit = option("standard", "Mit Text verschieben"); self.r_fest = option("standard", "Fester Text")
        g = QButtonGroup(self); g.addButton(self.r_mit); g.addButton(self.r_fest)
        (self.r_mit if mit_text else self.r_fest).setChecked(True)
        self.r_mit.toggled.connect(self.verschieben)
        v.addWidget(self.r_mit); v.addWidget(self.r_fest)
        m = knopf("standard", "Mehr anzeigen", ohne_rand=True, hand=True)
        m.setProperty("dropdownLink", True)
        m.clicked.connect(lambda: (self.close(), self.mehr.emit())); v.addWidget(m)
        self.setze(art)

    @staticmethod
    def _titel(text: str) -> QLabel:
        t = QLabel(text); t.setProperty("dropdownTitel", "abschnitt")
        return t

    def _klick(self, art: str) -> None:
        self.setze(art); self.gewaehlt.emit(art)

    def setze(self, art: str) -> None:
        self.zeile.setze(art if art == "textfluss" else None)
        self.umbruch.setze(art if art != "textfluss" else None)

    def zeigen_bei(self, pos: QPoint) -> None:
        self.adjustSize(); self.move(pos); self.show()
