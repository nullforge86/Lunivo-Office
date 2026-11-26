"""Das Absatz-Symbol links vom aktiven Feld (Kopf- oder Fußzeile auf dem Blatt): Absatzformat zurücksetzen, Symbol ausblenden.

Knopf und Einträge stehen in ``writer`` (``blattknoepfe.ABSATZ``, ``blattklappen.ABSATZ``)."""
from __future__ import annotations

from PySide6.QtWidgets import QWidget

from writer.funktionen.kopffuss import blattklappen as K, blattknoepfe
from vcl.qt.widgets.bausteine.farben import papierleiste
from vcl.qt.widgets.bausteine.zustaende.geruest import reihe
from vcl.qt.widgets.dokumentansicht.kopffuss import klappen
from vcl.qt.widgets.dokumentansicht.kopffuss.blattknopf import blattknopf
from vcl.qt.widgets.menues.dropdown import MenueListe


class KopfFussAbsatzKnopf(QWidget):
    def __init__(self, eltern: QWidget, bearbeiter):
        super().__init__(eltern)
        self.ausgeblendet = False                                # vom Benutzer ausgeblendet: bleibt weg, bis die Bearbeitung neu beginnt
        zeile = reihe("kein", self)
        knopf = blattknopf(blattknoepfe.ABSATZ)
        zeile.addWidget(knopf)
        papierleiste(self)
        m = MenueListe(eltern)
        knopf.setMenu(m)
        aktionen = {"zuruecksetzen": lambda: bearbeiter.ausrichtung_setzen(K.AUSRICHTUNG_VORGABE), "ausblenden": self._ausblenden}
        m.aboutToShow.connect(lambda: klappen.absatz(m, aktionen))
        self.adjustSize()

    def _ausblenden(self) -> None:
        self.ausgeblendet = True
        self.hide()
