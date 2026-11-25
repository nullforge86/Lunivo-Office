"""Randvorgaben-Steuerung für das Menüband."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtWidgets import QWidget

from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import werkzeugknopf

from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_ENG, BREITE_BAND_GRUPPENKNOPF, HOEHE_BAND_GRUPPENKNOPF, HOEHE_BAND_GRUPPENKNOPF_KOMPAKT, RAND_KEIN


class BandRaenderBaustein:
    """Erzeugt die Auswahl der vordefinierten Seitenränder."""

    def _raender(self) -> QWidget:
        host = QWidget()
        h = _reihe("eng", host)
        for art, text in self.b.galerie_randVorgaben():
            k = werkzeugknopf("fest", text, groesse=(BREITE_BAND_GRUPPENKNOPF, HOEHE_BAND_GRUPPENKNOPF_KOMPAKT if self.kompakt else HOEHE_BAND_GRUPPENKNOPF),
                              aktion=lambda a=art: (self.b.randVorgabeWaehlen(a), self.aktualisieren()))
            h.addWidget(k)
            self.knoepfe.append((k, None, True))
        return host
