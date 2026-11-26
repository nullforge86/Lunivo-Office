"""Aufklappfeld „Seitenzahl einfügen“: Format, Position (Kacheln mit Seitenbildchen), „Übernehmen für“ und OK.

Welche Formate, Positionen und Bereiche es gibt, steht in ``writer`` (``blattklappen``, ``seitenzahl.muster``); das Feld zeigt sie nur an und
meldet die Wahl mit ``uebernommen``."""
from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QButtonGroup, QComboBox, QLabel, QWidget, QWidgetAction

import vcl.qt.widgets.bausteine.interaktion.option as _option
from writer.anbindung import seitenzahl as _seitenzahl
from writer.funktionen.kopffuss import blattklappen as K, blatttexte as T
from vcl.qt.widgets.bausteine.abstaende import KOPFFUSS_KACHEL, KOPFFUSS_KACHEL_BILD
from vcl.qt.widgets.bausteine.farben import papierpanel
from vcl.qt.widgets.bausteine.interaktion.knopf import werkzeugknopf
from vcl.qt.widgets.bausteine.symbole.medien import seitenzahl_zeichner
from vcl.qt.widgets.bausteine.zustaende.geruest import reihe, spalte
from vcl.qt.widgets.menues.dropdown import MenueListe


class SeitenzahlPanel(MenueListe):
    uebernommen = Signal(str, str, str, str)          # Ausrichtung, Muster, Zahlenart, Bereich

    def __init__(self, eltern: QWidget):
        super().__init__(eltern)
        inhalt = QWidget()
        v = spalte("panel", inhalt)
        self.format = QComboBox()
        self.format.setAccessibleName(T.PANEL_FORMAT)
        for muster, zahl, text in _seitenzahl.muster():
            self.format.addItem(T.PANEL_FORMAT + ": " + text, (muster, zahl))
        v.addWidget(self.format)
        v.addWidget(QLabel(T.PANEL_POSITION))
        self.kacheln = self._kacheln(v)
        v.addWidget(QLabel(T.PANEL_BEREICH))
        self.bereich = self._bereiche(v)
        fuss = reihe("kein")
        fuss.addStretch(1)
        ok = werkzeugknopf("standard", T.PANEL_OK, aktion=self._ok, flach=False)
        fuss.addWidget(ok)
        v.addLayout(fuss)
        papierpanel(self, inhalt, ok)                            # gehört zur Leiste auf dem weißen Papier: unabhängig vom Thema
        aktion = QWidgetAction(self)
        aktion.setDefaultWidget(inhalt)
        self.addAction(aktion)

    def _kacheln(self, v) -> dict:
        """Je Position eine umschaltbare Kachel, in den Reihen der Beschreibung; genau eine ist gewählt."""
        gruppe = QButtonGroup(self)
        gruppe.setExclusive(True)
        kacheln = {}
        for zeile in K.POSITIONEN:
            h = reihe("eng")
            for schluessel, text in zeile:
                kacheln[schluessel] = werkzeugknopf("band_stil", text, groesse=KOPFFUSS_KACHEL, umschaltbar=True, an=schluessel == K.POSITION_VORGABE,
                                                    name=text, flach=False)
                gruppe.addButton(kacheln[schluessel])
                h.addWidget(kacheln[schluessel])
            h.addStretch(1)
            v.addLayout(h)
        return kacheln

    def _bereiche(self, v) -> dict:
        gruppe = QButtonGroup(self)
        bereich = {}
        h = reihe("inhalt")
        for schluessel, text in K.BEREICHE:
            bereich[schluessel] = _option.option("standard", text, an=schluessel == K.BEREICH_VORGABE, gruppe=gruppe)
            h.addWidget(bereich[schluessel])
        v.addLayout(h)
        return bereich

    def ort_setzen(self, ort: str) -> None:
        """Die Seitenbildchen der Kacheln für Kopf- oder Fußzeile zeichnen."""
        breite, hoehe = KOPFFUSS_KACHEL_BILD
        for schluessel, k in self.kacheln.items():
            bild = QPixmap(breite, hoehe)
            bild.fill(Qt.transparent)
            p = QPainter(bild)
            p.setRenderHint(QPainter.Antialiasing)
            seitenzahl_zeichner(ort, schluessel)(p, QRectF(0, 0, breite, hoehe))
            p.end()
            k.setIcon(QIcon(bild))
            k.setIconSize(QSize(breite, hoehe))

    def _ok(self) -> None:
        position = next(s for s, k in self.kacheln.items() if k.isChecked())
        bereich = next(s for s, o in self.bereich.items() if o.isChecked())
        muster, zahl = self.format.currentData()
        self.close()
        self.uebernommen.emit(position, muster, zahl, bereich)
