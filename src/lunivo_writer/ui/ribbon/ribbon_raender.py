"""Randvorgaben-Steuerung für das Menüband."""
from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QToolButton, QWidget

from lunivo_writer.ui.baukasten.mass import (
    ABSTAND_ENG, BREITE_BAND_GRUPPENKNOPF,
    HOEHE_BAND_GRUPPENKNOPF, HOEHE_BAND_GRUPPENKNOPF_KOMPAKT,
    RAND_KEIN,
)


class BandRaenderBaustein:
    """Erzeugt die Auswahl der vordefinierten Seitenränder."""

    def _raender(self) -> QWidget:
        host = QWidget()
        h = QHBoxLayout(host)
        h.setContentsMargins(*RAND_KEIN)
        h.setSpacing(ABSTAND_ENG)
        for art, text in self.b.galerie_randVorgaben():
            k = QToolButton()
            k.setAutoRaise(True)
            k.setText(text)
            k.setFixedSize(BREITE_BAND_GRUPPENKNOPF, HOEHE_BAND_GRUPPENKNOPF_KOMPAKT if self.kompakt else HOEHE_BAND_GRUPPENKNOPF)
            k.clicked.connect(lambda _=False, a=art: (self.b.randVorgabeWaehlen(a), self.aktualisieren()))
            h.addWidget(k)
            self.knoepfe.append((k, None, True))
        return host
