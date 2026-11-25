"""Polster dialog: aus ``vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QDialog
from vcl.qt.rendering.formen import Linie
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import VorschauFlaeche, fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.mass_feld import _PT_MM, EinheitFeld
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_RAHMENABSTAND, HOEHE_BEREICH_MITTEL
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
from vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung_hilfen import _blatt_vorschau


class _PolsterDialog(QDialog):
    """„Optionen …“ am Absatzrahmen: Abstand des Rahmens vom Text, oben, unten, links und rechts (mit Einheit), dazu eine Vorschau."""
    def __init__(self, parent, werte: tuple[float, float, float, float], linie: Linie | None = None):
        super().__init__(parent)
        self.setWindowTitle("Rahmen- und Schattierungsoptionen"); self.resize(*GROESSE_FENSTER_RAHMENABSTAND); self.setMinimumSize(0, 0)
        self._linie = linie
        v = _spalte("standard", self)
        v.addWidget(abschnittstitel("Vom Text"))
        g = FormularGitter()
        einh = ("pt", "mm", "cm", "in")
        self.felder = {}
        paare = []
        for name, schl, wert in (("Oben:", "o", werte[0]), ("Unten:", "u", werte[1]), ("Links:", "l", werte[2]), ("Rechts:", "r", werte[3])):
            f = EinheitFeld(wert * _PT_MM, 0.0, 31 * _PT_MM, einh, "pt"); self.felder[schl] = f
            paare.append((name, f))
            f.valueChanged.connect(lambda *_: self.vorschau.update())
        g.reihe(*paare)                                              # je nach Breite 2 bis 4 nebeneinander
        v.addLayout(g)
        v.addWidget(abschnittstitel("Vorschau"))
        self.vorschau = VorschauFlaeche(self._male, 150, flaeche=False); self.vorschau.setFixedHeight(HOEHE_BEREICH_MITTEL); v.addWidget(self.vorschau)
        v.addStretch(1)
        fussleiste(self, v)

    def werte(self) -> tuple[float, float, float, float]:
        f = self.felder
        return tuple(round(f[k].value() / _PT_MM, 2) for k in ("o", "u", "l", "r"))

    def _male(self, p, rect) -> None:
        """Ein Blatt mit Textzeilen; der Rahmen um den Absatz hat die eingestellten Abstände zum Text."""
        blatt, text = _blatt_vorschau(p, rect)
        o, u, l, rt = self.werte()
        k = 1.4                                                    # pt → Bildpunkte der Vorschau
        p.setPen(QPen(QColor(Farbe.TINTE_DUNKEL), 1)); p.setBrush(Qt.NoBrush)
        p.drawRect(QRectF(text.left() - l * k, text.top() - o * k, text.width() + (l + rt) * k, text.height() + (o + u) * k))
