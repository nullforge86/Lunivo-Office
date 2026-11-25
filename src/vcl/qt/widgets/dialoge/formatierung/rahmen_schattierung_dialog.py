"""Rahmen schattierung dialog: aus ``vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog
from vcl.qt.rendering.formen import Linie
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_RAHMEN_SCHATTIERUNG
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.interaktion.felder.angepasste_reiter import AngepassteReiter
from vcl.qt.widgets.dialoge.formatierung.rahmen_seite import _RahmenSeite
from vcl.qt.widgets.dialoge.formatierung.schattierung_seite import _SchattierungSeite


# ---------------------------------------------------------------------------------------------------------- Fenster
class RahmenSchattierungDialog(PanelFaehig, QDialog):
    """Das Fenster „Rahmen und Schattierung“. Die Reiter und ihre Werte stehen oben in der Beschreibung des Bausteins."""

    def __init__(self, parent=None, *, rahmen: Linie | None = None, fuell: str | None = None, muster: tuple[str, str] | None = None,
                 seitenrand: dict | None = None, mit_seitenrand: bool = True, fuer: list[str] | None = None, innen_h: bool = True,
                 seite: str = "rahmen"):
        super().__init__(parent)
        self.setWindowTitle("Rahmen und Schattierung")
        self.resize(*GROESSE_FENSTER_RAHMEN_SCHATTIERUNG)
        v = _spalte("standard", self)
        self.reiter = AngepassteReiter(); v.addWidget(self.reiter, 1)
        self.p_rahmen = _RahmenSeite(rahmen, innen_h=innen_h, fuer=fuer)
        self.reiter.addTab(self.p_rahmen, "Rahmen")
        self.p_rand = None
        if mit_seitenrand:
            sr = seitenrand or {}
            li = Linie(sr.get("farbe", Farbe.SCHWARZ), float(sr.get("breite_pt", 1.0)), sr.get("art", "einfach"), sr.get("seiten", "tblr")) if seitenrand else None
            self.p_rand = _RahmenSeite(li, seitenrand=True, fuer=["Gesamtes Dokument"], abstand_mm=float(sr.get("abstand_mm", 8.0)))
            if seitenrand:                                                                  # Optionen des vorhandenen Seitenrahmens
                from vcl.qt.rendering.formen.seitenrahmen import abstaende_pt
                self.p_rand.rand_optionen = {"messen": sr.get("messen", "seitenrand"), "abstand": abstaende_pt(sr), "ausrichten": bool(sr.get("ausrichten")),
                                             "vordergrund": sr.get("vordergrund", True), "kopf": bool(sr.get("kopf")), "fuss": bool(sr.get("fuss"))}
                self.p_rand.kunst.setCurrentIndex(max(0, self.p_rand.kunst.findData(sr.get("kunst", ""))))
                self.p_rand._abstand_vorschau()
            self.reiter.addTab(self.p_rand, "Seitenrand")
        self.p_schatt = _SchattierungSeite(fuell, muster, fuer)
        self.reiter.addTab(self.p_schatt, "Schattierung")
        self.reiter.setCurrentIndex({"rahmen": 0, "seitenrand": 1 if mit_seitenrand else 0}.get(seite, self.reiter.count() - 1))
        fussleiste(self, v)

    def passe_an(self, breite: int, hoehe: int) -> None:
        """Vorschau so groß, wie die Seitenleiste Platz hat (neben ihr stehen Farbe und Breite)."""
        for s in (self.p_rahmen, self.p_rand):
            if s is not None:
                s.kasten.setMaximal(184 if breite >= 400 else 152)

    # ---- Ergebnis
    def rahmen(self) -> Linie | None:
        s = self.p_rahmen.seiten
        return self.p_rahmen.linie_wert().mit_seiten(s) if s else None

    def schattierung(self) -> tuple[str | None, tuple[str, str] | None]:
        """(Füllfarbe oder None, (Musterschlüssel, Musterfarbe) oder None)."""
        return self.p_schatt.werte()

    def seitenrand(self) -> dict | None:
        if self.p_rand is None or not self.p_rand.seiten:
            return None
        li = self.p_rand.linie_wert()
        o = self.p_rand.rand_optionen
        erg = {"art": li.art, "farbe": li.farbe, "breite_pt": li.breite_pt, "abstand_mm": round(sum(o["abstand"]) / 4 / 72 * 25.4, 2),
               "seiten": "".join(c for c in "tblr" if c in self.p_rand.seiten), "messen": o["messen"], "abstand": ",".join(f"{x:g}" for x in o["abstand"]),
               "ausrichten": o["ausrichten"], "vordergrund": o["vordergrund"], "kopf": o["kopf"], "fuss": o["fuss"]}
        if self.p_rand.kunst.currentData():
            erg["kunst"] = self.p_rand.kunst.currentData()
        return erg
