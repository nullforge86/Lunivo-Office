"""Zwei kleine Bausteine für Erstellen-Fenster (Schnelle KI-Aktion, KI-Assistent): Vorlagen-Chips und ein aufklappbarer Bereich.

    chips = VorlagenChips(["Korrekturlesen", …]); chips.gewaehlt.connect(lambda i: …)   # sechs Chips, „Alle anzeigen“ zeigt den Rest
    bereich = AufklappBereich("Erweiterte Einstellungen")                              # ``FormularGitter(bereich.inhalt)`` füllen; Knopf „… anzeigen/ausblenden“
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.bausteine.knopf.knopf import knopf

from vcl.qt.widgets.bausteine.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QWidget

from vcl.qt.widgets.bausteine.felder.karten_raster import KartenRaster
from writer.baukasten.basis.mass import ABSTAND_KLEIN, ABSTAND_NORMAL, BREITE_RASTERZELLE_CHIP, RAND_KEIN
from vcl.qt.widgets.bausteine.basis.karte import als_karte


def _link(text: str = "") -> QPushButton:
    b = knopf("standard", text, ohne_rand=True, hand=True); b.setProperty("dropdownLink", True)
    return b


class VorlagenChips(QWidget):
    """Chips zum Antippen; zuerst ``zuerst`` Stück, mit „Alle anzeigen“ alle. Meldet den Index des gewählten Chips."""

    gewaehlt = Signal(int)

    def __init__(self, namen, zuerst: int = 6, parent=None):
        super().__init__(parent)
        self._zuerst = zuerst
        v = _spalte("eng", self)
        self.fluss = KartenRaster(min_breite=BREITE_RASTERZELLE_CHIP, abstand=ABSTAND_NORMAL, spanne_nach_inhalt=True, zeile_min=0)   # Chips im Raster: Spalten nach Textlänge
        v.addLayout(self.fluss)
        self.chips = []
        for i, n in enumerate(namen):
            b = knopf("standard", n); als_karte(b, "chip"); b.clicked.connect(lambda _=False, i=i: self.gewaehlt.emit(i))
            self.chips.append(b)
        self.mehr = _link(); self.mehr.clicked.connect(self.umschalten)
        v.addWidget(self.mehr, 0, Qt.AlignLeft)
        self.alle = False
        self.umschalten()

    def umschalten(self) -> None:
        self.alle = not self.alle
        while self.fluss.count():                                    # ausgeblendete Chips dürfen im Fluss keinen Platz belegen
            self.fluss.takeAt(0)
        for i, b in enumerate(self.chips):
            zeigen = self.alle or i < self._zuerst
            b.setVisible(zeigen)
            if zeigen:
                self.fluss.addWidget(b)
        self.mehr.setVisible(len(self.chips) > self._zuerst)
        self.mehr.setText("Ausblenden" if self.alle else "Alle anzeigen")
        self.fluss.invalidate()


class AufklappBereich(QWidget):
    """Ein Link-Knopf „<Titel> anzeigen/ausblenden“ und darunter ein Bereich, der aufklappt (``layout_innen``)."""

    def __init__(self, titel: str, parent=None):
        super().__init__(parent)
        self._titel = titel
        v = _spalte("eng", self)
        self.knopf = _link(); v.addWidget(self.knopf, 0, Qt.AlignLeft)
        self.inhalt = QWidget()                                       # der Aufrufer legt sein Layout (z. B. ``FormularGitter(bereich.inhalt)``) hinein
        v.addWidget(self.inhalt)
        self.knopf.clicked.connect(lambda: self.umschalten(not self.inhalt.isVisible()))
        self.umschalten(False)

    def umschalten(self, an: bool) -> None:
        self.inhalt.setVisible(an)
        self.knopf.setText(f"{self._titel} {'ausblenden' if an else 'anzeigen'}")
