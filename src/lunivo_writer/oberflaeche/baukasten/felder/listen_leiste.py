"""Liste mit Knopfleiste: der EINE Baustein für jede Liste, die man hinzufügen, bearbeiten und entfernen kann (KI-Modelle, KI-Werkzeuge …).

    ListenLeiste(neu_tip="Anbieter hinzufügen", min_hoehe=HOEHE_LISTE_MITTEL)
        .liste                          # die QListWidget (Eintrag mit ``Qt.UserRole``-Daten), Rahmen und Zeilen vom Thema
        .neu_angefordert / .bearbeiten_angefordert / .entfernen_angefordert     # Signale; Doppelklick auf einen Eintrag = bearbeiten
        .knoepfe_pruefen()              # Stift und Papierkorb nur bei gewähltem Eintrag (folgt ``currentRowChanged`` selbst; nach dem Füllen aufrufen)

Liste und Leiste sind eine Fläche: EIN Rahmen (``karte="listenleiste"``), unter der Liste eine Trennlinie, darin die Knöpfe. Stil nur im Thema (``karte.py``)."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QListWidget, QToolButton, QVBoxLayout

from lunivo_writer.oberflaeche.baukasten.basis.karte import als_karte
from lunivo_writer.oberflaeche.baukasten.basis.mass import ABSTAND_KLEIN, BREITE_KNOPF_KLEIN, HOEHE_KNOPF_GROSS, HOEHE_LISTE_MITTEL, ICON_NORMAL, RAND_KEIN
from lunivo_writer.oberflaeche.bauteile import symbole


class ListenLeiste(QFrame):
    neu_angefordert = Signal()
    bearbeiten_angefordert = Signal()
    entfernen_angefordert = Signal()

    def __init__(self, neu_tip: str = "Hinzufügen", min_hoehe: int = HOEHE_LISTE_MITTEL, parent=None):
        super().__init__(parent)
        als_karte(self, "listenleiste")
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN); v.setSpacing(0)
        self.liste = QListWidget(); self.liste.setMinimumHeight(min_hoehe)
        als_karte(self.liste, "liste")
        v.addWidget(self.liste, 1)
        fuss = QFrame(); als_karte(fuss, "listenfuss")
        h = QHBoxLayout(fuss); h.setContentsMargins(ABSTAND_KLEIN, ABSTAND_KLEIN, ABSTAND_KLEIN, ABSTAND_KLEIN); h.setSpacing(ABSTAND_KLEIN)
        self.neu = self._knopf("plus", neu_tip)
        self.bearb = self._knopf("pencil", "Bearbeiten")
        self.weg = self._knopf("trash-2", "Entfernen")
        for b in (self.neu, self.bearb, self.weg):
            h.addWidget(b)
        h.addStretch(1)
        v.addWidget(fuss)
        self.neu.clicked.connect(self.neu_angefordert)
        self.bearb.clicked.connect(self.bearbeiten_angefordert)
        self.weg.clicked.connect(self.entfernen_angefordert)
        self.liste.currentRowChanged.connect(self.knoepfe_pruefen)
        self.liste.itemDoubleClicked.connect(lambda _i: self.bearbeiten_angefordert.emit())
        self.knoepfe_pruefen()

    @staticmethod
    def _knopf(symbol: str, tip: str) -> QToolButton:
        b = QToolButton(); b.setIcon(symbole.icon(symbol, ICON_NORMAL)); b.setToolTip(tip); b.setAccessibleName(tip)
        b.setMinimumSize(BREITE_KNOPF_KLEIN, HOEHE_KNOPF_GROSS); b.setFocusPolicy(Qt.TabFocus)
        return b

    def knoepfe_pruefen(self, *_) -> None:
        an = self.liste.currentRow() >= 0
        self.bearb.setEnabled(an); self.weg.setEnabled(an)
