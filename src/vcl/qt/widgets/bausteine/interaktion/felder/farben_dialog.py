"""Farben dialog: aus ``vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialog, QSlider, QSpinBox, QWidget
from vcl.qt.widgets.bausteine.abstaende.mass import RAND_FARBWAEHLER_TRANSPARENZ
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
from vcl.qt.widgets.bausteine.interaktion.felder.angepasste_reiter import AngepassteReiter
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, mittig
from vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler_hilfen import Modell, _FlaechePaar, _Leiste, _ProbeBlock, _Proben
from vcl.qt.widgets.bausteine.interaktion.felder.flaeche import _Flaeche
from vcl.qt.widgets.bausteine.interaktion.felder.kacheln import _Kacheln
from vcl.qt.widgets.bausteine.interaktion.felder.regler import _Regler
from vcl.qt.widgets.bausteine.interaktion.felder.ring import _Ring


class FarbenDialog(PanelFaehig, QDialog):
    """Das Fenster „Farben“ (öffnet sich in der Seitenleiste). ``farbe()`` gibt nach OK die gewählte Farbe zurück."""

    def __init__(self, parent=None, start=None, titel: str = "Farben"):
        super().__init__(parent)
        self.setWindowTitle(titel if titel not in ("", "Farbe") else "Farben")
        ausgang = QColor(start) if start is not None and QColor(start).isValid() else QColor(Farbe.SCHWARZ)
        self.m = Modell(ausgang)
        self.m.deckkraft = round(ausgang.alphaF() * 100)
        v = _spalte("standard", self)
        self.reiter = AngepassteReiter()                                  # Standard braucht weniger Platz als Erweitert
        v.addWidget(self.reiter, 1)

        def seite(inhalt: QWidget, regler: bool) -> QWidget:
            w = QWidget(); sv = _spalte("panel", w)
            sv.addWidget(inhalt, 0, Qt.AlignHCenter)
            if regler:
                sv.addWidget(_Regler(self.m))
            sv.addStretch(1)
            return w
        kacheln = self._kacheln = _Kacheln(self.m)
        kacheln.bestaetigt.connect(self.accept)
        self._flaeche, self._leiste = _Flaeche(self.m), _Leiste(self.m)
        flaeche = self._paar = _FlaechePaar(self._flaeche, self._leiste)
        self.reiter.addTab(seite(kacheln, False), "Standard")
        self.reiter.addTab(seite(flaeche, True), "Benutzerdefiniert")
        self._ring = _Ring(self.m)
        self.reiter.addTab(seite(self._ring, True), "Erweitert")
        # Neu und Aktuell: die Probe mit ihren Beschriftungen, mittig unter den Reitern
        v.addWidget(mittig(_ProbeBlock(_Proben(self.m, ausgang))))           # mittig unter den Farben
        v.addWidget(self._transparenz_zeile())
        v.addWidget(knopfzeile(self))

    def _transparenz_zeile(self) -> QWidget:
        """„Transparenz“: Schieber und Zahlenfeld in Prozent (100 % = deckend) — beide halten dieselbe Zahl."""
        z = QWidget(); zg = FormularGitter(z); zg.setContentsMargins(*RAND_FARBWAEHLER_TRANSPARENZ)
        self.schieber = QSlider(Qt.Horizontal); self.schieber.setRange(0, 100); self.schieber.setValue(self.m.deckkraft)
        self.prozent = QSpinBox(); self.prozent.setRange(0, 100); self.prozent.setSuffix(" %"); self.prozent.setValue(self.m.deckkraft)
        self.schieber.setToolTip("100 % = deckend, 0 % = unsichtbar"); self.prozent.setToolTip(self.schieber.toolTip())
        self.schieber.valueChanged.connect(self.m.setze_deckkraft); self.prozent.valueChanged.connect(self.m.setze_deckkraft)
        self.m.geaendert.connect(self._deckkraft_zeigen)
        zg.reihe(("Transparenz", self.schieber), ("Prozent", self.prozent), gewichte=(2, 1))
        return z

    def _deckkraft_zeigen(self) -> None:
        for w in (self.schieber, self.prozent):
            if w.value() != self.m.deckkraft:
                w.blockSignals(True); w.setValue(self.m.deckkraft); w.blockSignals(False)

    def passe_an(self, breite: int, hoehe: int) -> None:
        """Das Standard-Raster so groß machen, wie die Seitenleiste Platz hat (Breite für 17 Spalten, Höhe für 18 Zeilen samt Reitern und Probe)."""
        k = self._kacheln
        zelle = min((breite - 40) // k.SPALTEN - 1, (hoehe - 250) // (k.ZEILEN + 2) - 1)
        k.skaliere(max(12, min(24, zelle)))
        h = max(120, min(340, hoehe - 400))                                         # Farbfläche und Leiste: die Höhe, die nach den zwei Reihen Felder und der Probe übrig bleibt
        self._leiste.setFixedHeight(h); self._flaeche.setGroesse(max(200, min(380, breite - 100)), h); self._paar.ordne()
        self._ring.skaliere(max(0.7, min(1.5, (hoehe - 400) / 250, (breite - 40) / 270)))

    def farbe(self) -> QColor:
        """Die gewählte Farbe samt Transparenz (Alpha); ohne Änderung am Schieber ist sie deckend."""
        c = self.m.farbe(); c.setAlphaF(self.m.deckkraft / 100)
        return c

    def deckkraft(self) -> int:
        return self.m.deckkraft
