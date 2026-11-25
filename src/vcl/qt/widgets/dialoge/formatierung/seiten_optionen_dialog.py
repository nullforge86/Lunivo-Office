"""Seiten optionen dialog: aus ``vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QDialog
from vcl.qt.rendering.formen import Linie
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import VorschauFlaeche, fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.mass_feld import _PT_MM, EinheitFeld
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_SEITENRAND, HOEHE_BEREICH_MITTEL
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter, abschnittstitel
from vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung_hilfen import _blatt_vorschau


class _SeitenOptionenDialog(QDialog):
    """„Optionen …“ am Seitenrand: Abstand (vom Text oder vom Seitenrand), „Gemessen von“, die vier Optionen und eine Vorschau der Seite."""
    def __init__(self, parent, w: dict, linie: Linie | None = None):
        super().__init__(parent)
        self.setWindowTitle("Rahmen- und Schattierungsoptionen"); self.resize(*GROESSE_FENSTER_SEITENRAND); self.setMinimumSize(0, 0)
        v = _spalte("standard", self)
        self.abstand_gruppe = abschnittstitel("Vom Text"); v.addWidget(self.abstand_gruppe)
        g = FormularGitter()
        einh = ("pt", "mm", "cm", "in")
        o, u, l, r = w["abstand"]
        self.felder = {}
        paare = []
        for name, schl, wert in (("Oben:", "o", o), ("Unten:", "u", u), ("Links:", "l", l), ("Rechts:", "r", r)):
            f = EinheitFeld(wert * _PT_MM, 0.0, 31 * _PT_MM, einh, "pt"); self.felder[schl] = f
            paare.append((name, f))
            f.valueChanged.connect(lambda *_: self.vorschau.update())
        g.reihe(*paare)
        self.messen = Auswahlfeld(); self.messen.addItem("Text", "text"); self.messen.addItem("Seitenrand", "seitenrand")
        self.messen.setCurrentIndex(0 if w["messen"] == "text" else 1)
        self.messen.currentIndexChanged.connect(self._messen)
        g.reihe(("Gemessen von:", self.messen))
        v.addLayout(g)
        v.addWidget(abschnittstitel("Optionen"))
        self.ausrichten = UmbruchSchalter("Absatzrahmen und Tabellenränder am Seitenrand ausrichten"); self.ausrichten.setChecked(w["ausrichten"])
        self.vordergrund = UmbruchSchalter("Immer im Vordergrund anzeigen"); self.vordergrund.setChecked(w["vordergrund"])
        self.kopf = UmbruchSchalter("Kopfzeile umgeben"); self.kopf.setChecked(w["kopf"])
        self.fuss = UmbruchSchalter("Fußzeile umgeben"); self.fuss.setChecked(w["fuss"])
        og = FormularGitter()
        for c in (self.ausrichten, self.vordergrund, self.kopf, self.fuss):
            og.breit(c)
        v.addLayout(og)
        v.addWidget(abschnittstitel("Vorschau"))
        self.vorschau = VorschauFlaeche(self._male, 150, flaeche=False); self.vorschau.setFixedHeight(HOEHE_BEREICH_MITTEL); v.addWidget(self.vorschau)
        v.addStretch(1)
        self._linie = linie
        for c in (self.ausrichten, self.vordergrund, self.kopf, self.fuss):
            c.toggled.connect(lambda *_: self.vorschau.update())
        fussleiste(self, v)
        self._messen()

    def _messen(self, *_) -> None:
        text = self.messen.currentData() == "text"
        self.abstand_gruppe.setText("VOM TEXT" if text else "VOM SEITENRAND")
        self.kopf.setEnabled(text); self.fuss.setEnabled(text)             # Kopf- und Fußzeile gehören zum Text-Bezug
        self.vorschau.update()

    def werte(self) -> dict:
        f = self.felder
        return {"messen": self.messen.currentData(), "abstand": tuple(round(f[k].value() / _PT_MM, 2) for k in ("o", "u", "l", "r")),
                "ausrichten": self.ausrichten.isChecked(), "vordergrund": self.vordergrund.isChecked(), "kopf": self.kopf.isChecked(), "fuss": self.fuss.isChecked()}

    def _male(self, p, rect) -> None:
        """Ein Blatt mit Text; der Rahmen liegt je nach „Gemessen von“ um den Text oder am Blattrand."""
        blatt, text = _blatt_vorschau(p, rect)
        w = self.werte()
        o, u, l, rt = (x * 1.2 for x in w["abstand"])
        p.setPen(QPen(QColor(Farbe.TINTE_DUNKEL), 1)); p.setBrush(Qt.NoBrush)
        if w["messen"] == "text":
            p.drawRect(QRectF(text.left() - l, text.top() - o, text.width() + l + rt, text.height() + o + u))
        else:
            p.drawRect(QRectF(blatt.left() + l, blatt.top() + o, blatt.width() - l - rt, blatt.height() - o - u))
