"""Tabellen eigenschaften dialog: aus ``vcl.qt.widgets.dialoge.dokument_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog, QDoubleSpinBox, QSpinBox, QWidget
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter, abschnittstitel
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld


class TabellenEigenschaftenDialog(PanelFaehig, QDialog):
    """„Tabelleneigenschaften“ (Reiter „Tabelle“ und „Spalte und Zelle“). Ändert die Tabelle nicht selbst; der Aufrufer liest ``werte()``
    (Format wie ``editor.tabelle.tabelleneigenschaften.lesen``) oder die alten Felder breite/ausr/rand/pad/kopf.

    ``werte`` (optional) überschreibt die Einzelargumente; fehlende Schlüssel stammen aus ``VORGABE``."""
    AUSRICHTUNGEN = ("Links", "Zentriert", "Rechts")
    _AUSR = ("links", "mitte", "rechts")
    _PT_MM = 25.4 / 72
    _PX_MM = 25.4 / 96

    def __init__(self, parent, breite_prozent: int = 100, ausrichtung: int = 0, rand: float = 1.0, abstand: float = 4.0,
                 kopfzeile: bool = False, *, werte: dict | None = None):
        super().__init__(parent)
        from core.tabellen.modell.tabelleneigenschaften import VORGABE
        from vcl.qt.widgets.bausteine.interaktion.felder.angepasste_reiter import AngepassteReiter
        from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter, abschnittstitel
        from vcl.qt.widgets.bausteine.interaktion.felder.mass_feld import EinheitFeld
        self.setWindowTitle("Tabelleneigenschaften")
        v = _spalte("standard", self)
        self.reiter = AngepassteReiter(); v.addWidget(self.reiter, 1)
        # ---- Tabelle
        s = QWidget(); g = FormularGitter(s)
        self.art = Auswahlfeld()
        for k, n in (("auto", "Automatisch"), ("prozent", "Prozent des Textbereichs"), ("fest", "Feste Breite")):
            self.art.addItem(n, k)
        self.breite = QSpinBox(); self.breite.setRange(10, 100); self.breite.setSuffix(" %")
        self.fest = EinheitFeld(0.0, 5.0, 1000.0, ("mm", "cm", "in"), "cm")
        self.ausr = Auswahlfeld(); self.ausr.addItems(self.AUSRICHTUNGEN)
        g.zeile("Breite", self.art)
        g.reihe(("Prozent", self.breite), ("Feste Breite", self.fest))
        g.zeile("Ausrichtung", self.ausr)
        g.breit(abschnittstitel("Zellen"))
        self.rand = QDoubleSpinBox(); self.rand.setRange(0, 15); self.rand.setDecimals(3); self.rand.setSingleStep(0.25); self.rand.setSuffix(" pt")
        self.pad = QDoubleSpinBox(); self.pad.setRange(0, 100); self.pad.setDecimals(3); self.pad.setSuffix(" px")
        self.abstand = EinheitFeld(0.0, 0.0, 50.0, ("mm", "cm", "pt"), "mm")
        g.reihe(("Rahmenstärke", self.rand), ("Innenabstand", self.pad))
        g.zeile("Zellenabstand", self.abstand)
        self.kopf = UmbruchSchalter("Erste Zeile ist Kopfzeile (wiederholt sich auf jeder Seite)"); self.kopf.setChecked(kopfzeile)
        g.breit(self.kopf)
        self.reiter.addTab(s, "Tabelle")
        # ---- Spalte und Zelle (die der Schreibmarke)
        z = QWidget(); zg = FormularGitter(z)
        self.sp_fest = UmbruchSchalter("Bevorzugte Breite der Spalte"); self.spalte = EinheitFeld(0.0, 5.0, 1000.0, ("mm", "cm", "in"), "cm")
        zg.breit(abschnittstitel("Spalte")); zg.breit(self.sp_fest); zg.zeile("Breite", self.spalte)
        zg.breit(abschnittstitel("Zelle"))
        self.senkrecht = Auswahlfeld()
        for k, n in (("oben", "Oben"), ("mitte", "Mittig"), ("unten", "Unten")):
            self.senkrecht.addItem(n, k)
        zg.zeile("Senkrechte Ausrichtung", self.senkrecht)
        self.reiter.addTab(z, "Spalte und Zelle")
        fussleiste(self, v)
        # ---- Startwerte
        w = {**VORGABE, "breite": float(breite_prozent), "ausr": self._AUSR[max(0, min(2, ausrichtung))],
             "rahmen": rand * self._PT_MM, "innen": abstand * self._PX_MM, **(werte or {})}
        self.setze(w)
        self.art.currentIndexChanged.connect(self._sichtbar); self._sichtbar()

    def setze(self, w: dict) -> None:
        a = w.get("breite_art", "prozent")
        self.art.setCurrentIndex(max(0, self.art.findData(a)))
        if a == "prozent":
            self.breite.setValue(int(round(w["breite"])))
        elif a == "fest":
            self.fest.setValue(w["breite"])
        self.ausr.setCurrentIndex(max(0, self._AUSR.index(w["ausr"]) if w["ausr"] in self._AUSR else 0))
        self.rand.setValue(w["rahmen"] / self._PT_MM); self.pad.setValue(w["innen"] / self._PX_MM)
        self.abstand.setValue(w["abstand"])
        self.sp_fest.setChecked(bool(w["spalte_fest"])); self.spalte.setValue(w["spalte"] or 30.0)
        self.senkrecht.setCurrentIndex(max(0, self.senkrecht.findData(w["senkrecht"])))

    def _sichtbar(self, *_) -> None:
        a = self.art.currentData()
        self.breite.setEnabled(a == "prozent"); self.fest.setEnabled(a == "fest")

    def werte(self) -> dict:
        a = self.art.currentData()
        return {"breite_art": a, "breite": float(self.breite.value()) if a == "prozent" else self.fest.value() if a == "fest" else 0.0,
                "ausr": self._AUSR[self.ausr.currentIndex()], "innen": self.pad.value() * self._PX_MM,
                "abstand": self.abstand.value(), "rahmen": self.rand.value() * self._PT_MM,
                "spalte_fest": self.sp_fest.isChecked(), "spalte": self.spalte.value(), "senkrecht": self.senkrecht.currentData()}
