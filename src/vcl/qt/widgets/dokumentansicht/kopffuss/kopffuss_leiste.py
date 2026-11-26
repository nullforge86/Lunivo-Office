"""Die Leiste neben dem Etikett des aktiven Bereichs (Kopf- oder Fußzeile auf dem Blatt).

Welche Knöpfe es gibt und wann sie erscheinen, steht in ``writer`` (``blattknoepfe.LEISTE``); ihre Klappen füllt ``klappen.py``, das Feld
„Seitenzahl einfügen“ ist ``seitenzahl_panel.py``. Die Leiste setzt nur zusammen."""
from __future__ import annotations

from PySide6.QtWidgets import QWidget

from writer.funktionen.kopffuss import blattknoepfe
from vcl.qt.widgets.bausteine.farben import papierleiste
from vcl.qt.widgets.bausteine.zustaende.geruest import reihe
from vcl.qt.widgets.dokumentansicht.kopffuss import klappen
from vcl.qt.widgets.dokumentansicht.kopffuss.blattknopf import blattknopf
from vcl.qt.widgets.dokumentansicht.kopffuss.seitenzahl_panel import SeitenzahlPanel
from vcl.qt.widgets.menues.dropdown import MenueListe


class KopfFussLeiste(QWidget):
    """``bearbeiter``: der ``KopfFussBearbeiter``, den die Klappen aufrufen."""

    def __init__(self, eltern: QWidget, bearbeiter):
        super().__init__(eltern)
        zeile = reihe("eng", self)
        self.knopf = {}
        self._mit_seitenzahl = {}
        for beschreibung in blattknoepfe.LEISTE:
            k = self.knopf[beschreibung.schluessel] = blattknopf(beschreibung)
            self._mit_seitenzahl[beschreibung.schluessel] = beschreibung.mit_seitenzahl
            zeile.addWidget(k)
            fuellen = klappen.FUELLER.get(beschreibung.schluessel)
            if fuellen is not None:
                m = MenueListe(eltern)
                k.setMenu(m)
                m.aboutToShow.connect(lambda m=m, fuellen=fuellen: fuellen(m, bearbeiter))
            else:                                                 # „Seitenzahl einfügen“: das Aufklappfeld
                self.panel = SeitenzahlPanel(eltern)
                k.setMenu(self.panel)
                self.panel.aboutToShow.connect(lambda: self.panel.ort_setzen(bearbeiter.zone))
                self.panel.uebernommen.connect(bearbeiter.seitenzahl_einfuegen)
        papierleiste(self)                                       # sitzt auf dem weißen Papier: unabhängig vom Thema
        self.zahl_zeigen(False)

    def zahl_zeigen(self, mit: bool) -> None:
        """Die Knöpfe zeigen, die zur Zeile passen: mit oder ohne Seitenzahl."""
        for schluessel, k in self.knopf.items():
            k.setVisible(self._mit_seitenzahl[schluessel] == mit)
        self.adjustSize()
