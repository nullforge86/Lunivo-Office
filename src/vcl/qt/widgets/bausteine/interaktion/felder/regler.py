"""Regler: aus ``vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QSpinBox, QWidget
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.interaktion.felder.farbwaehler_hilfen import Modell


MODELLE = ("RGB", "HSV", "HSL")


# ----------------------------------------------------------------------------------------- Farbmodell und Felder
class _Regler(QWidget):
    """Farbmodell (RGB, HSV, HSL), drei Zahlenfelder und die Schreibweise #rrggbb — gleich in allen Karteireitern."""
    def __init__(self, modell: Modell):
        super().__init__()
        self.m = modell
        self.modell_wahl = Auswahlfeld(); self.modell_wahl.addItems(MODELLE)
        self.namen = [QLabel() for _ in range(3)]
        self.felder = [QSpinBox() for _ in range(3)]
        self.hex = zeilenfeld("frei", platzhalter="#rrggbb"); self.hex.setMaxLength(7)
        # Rasteransicht des Baukastens: je nach Breite zwei Paare nebeneinander oder eines je Zeile, nichts ragt heraus
        g = FormularGitter(self)
        g.reihe(("Farbmodell", self.modell_wahl), ("Hex", self.hex))
        g.reihe(*zip(self.namen, self.felder))                               # die drei Werte nebeneinander, bei Platzmangel darunter
        for f in self.felder:
            f.valueChanged.connect(self._tippen)
        for w in (self.modell_wahl, self.hex, *self.felder):
            w.setMinimumWidth(0)
        self.modell_wahl.currentTextChanged.connect(self._modus)
        self.hex.editingFinished.connect(self._hex)
        self.m.geaendert.connect(self.auffrischen)
        self.m.modus_geaendert.connect(self._modus_zeigen)
        self._modus_zeigen()

    def _modus(self, text: str) -> None:
        if text != self.m.modus:
            self.m.modus = text
            self.m.modus_geaendert.emit()

    def _modus_zeigen(self) -> None:
        self.modell_wahl.blockSignals(True); self.modell_wahl.setCurrentText(self.m.modus); self.modell_wahl.blockSignals(False)
        namen = {"RGB": ("Rot", "Grün", "Blau"), "HSV": ("Farbton", "Sättigung", "Wert"), "HSL": ("Farbton", "Sättigung", "Helligkeit")}[self.m.modus]
        grenzen = {"RGB": ((0, 255),) * 3, "HSV": ((0, 359), (0, 100), (0, 100)), "HSL": ((0, 359), (0, 100), (0, 100))}[self.m.modus]
        for n, f, name, (lo, hi) in zip(self.namen, self.felder, namen, grenzen):
            n.setText(name); f.blockSignals(True); f.setRange(lo, hi); f.blockSignals(False)
        self.auffrischen()

    def werte(self) -> tuple[int, int, int]:
        c = self.m.farbe()
        if self.m.modus == "RGB":
            return c.red(), c.green(), c.blue()
        if self.m.modus == "HSV":
            return round(self.m.h * 359), round(self.m.s * 100), round(self.m.v * 100)
        h, s, l, _ = c.getHslF()
        return round((h if h >= 0 else self.m.h) * 359), round(s * 100), round(l * 100)

    def auffrischen(self) -> None:
        for f, w in zip(self.felder, self.werte()):
            f.blockSignals(True); f.setValue(w); f.blockSignals(False)
        self.hex.setText(self.m.farbe().name())

    def _tippen(self) -> None:
        a, b, c = (f.value() for f in self.felder)
        if self.m.modus == "RGB":
            self.m.setze(QColor(a, b, c))
        elif self.m.modus == "HSV":
            self.m.setze_hsv(h=a / 359 * 0.9999, s=b / 100, v=c / 100)
        else:
            self.m.setze(QColor.fromHslF(min(a / 359, 0.9999), b / 100, c / 100))

    def _hex(self) -> None:
        t = self.hex.text().strip()
        c = QColor(t if t.startswith("#") else "#" + t)
        if c.isValid():
            self.m.setze(c)
        else:
            self.auffrischen()
