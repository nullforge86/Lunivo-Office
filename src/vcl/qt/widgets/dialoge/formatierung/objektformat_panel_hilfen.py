"""Objektformat panel hilfen: aus ``vcl.qt.widgets.dialoge.formatierung.objektformat_panel`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget
from vcl.qt.rendering import formen as BE
from writer.funktionen.objekte import bildeffekte as BEW
from vcl.qt.widgets.bausteine.interaktion.felder.schiebe_feld import SchiebeFeld
from vcl.qt.widgets.dialoge.formatierung.texteffekt_dialog_hilfen import Abschnitt, seitengitter
from vcl.qt.widgets.dialoge.formatierung.texteffekt_panel import TexteffektPanel
from vcl.qt.widgets.menues.dropdown.voreinstellung_menue import VoreinstellungMenue
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_ABSCHLUSS_KACHEL


class _Felder(QWidget):
    """Eine Gruppe von Feldern im ``FormularGitter`` (Beschriftung über dem Feld), die nur bei passender Füllungs- oder Linienart zu sehen ist."""

    def __init__(self):
        super().__init__()
        self.gitter = seitengitter(self)

    def zeile(self, text: str, widget: QWidget) -> None:
        self.gitter.zeile(text, widget)

    def breit(self, widget: QWidget) -> None:
        self.gitter.breit(widget)


class _DreiDUntereinander:
    """Für beide Seiten der Effekte (Objekt und Text): Zahlenfelder als Regler mit Wert darüber (ein Schrittfeld zeigt seine Zahl im dunklen Thema nicht)
    und das 3D-Format mit den Feldern untereinander im ``FormularGitter`` — die Zweierreihen des Text-Panels sind für 300 px zu breit."""

    @staticmethod
    def _schritt_feld(lo: float, hi: float, suffix: str, schritt: float, nk: int) -> QWidget:
        return SchiebeFeld(lo, hi, suffix, schritt, nk)

    MIT_ABSCHLUSS = False                      # Oberer/Unterer Abschluss gibt es nur für Objekte (der Text-Effekt kennt sie nicht)

    def _seite_effekte(self, w: dict) -> QWidget:
        seite = super()._seite_effekte(w)
        # 3D-Format neu ordnen: die Felder untereinander im FormularGitter (die Zweierreihen des Text-Panels sind für 300 px zu breit)
        alt = self.a_3d
        self.a_3d = Abschnitt("3D-Format")
        zr3 = knopf("standard", "Zurücksetzen", aktion=self._d3_zuruecksetzen)
        self._ab_stumm = True
        self.ab_art, self.ab_knopf, self.ab_breite, self.ab_hoehe = {}, {}, {}, {}
        if self.MIT_ABSCHLUSS:
            for k, titel in (("oben", "Oberer Abschluss"), ("unten", "Unterer Abschluss")):
                self.ab_art[k] = "keine"
                self.ab_knopf[k] = knopf("standard", "Keine"); self.ab_knopf[k].setMinimumWidth(0)
                self.ab_breite[k], self.ab_hoehe[k] = SchiebeFeld(0, 20, " pt", 0.5, 1, 4.0), SchiebeFeld(0, 20, " pt", 0.5, 1, 6.0)
                self.a_3d.zeile(titel + ":", self.ab_knopf[k]); self.a_3d.zeile("Breite:", self.ab_breite[k]); self.a_3d.zeile("Höhe:", self.ab_hoehe[k])
                self.ab_knopf[k].clicked.connect(lambda _=False, k=k: self._abschluss_menue(k))
                for f in (self.ab_breite[k], self.ab_hoehe[k]):
                    f.valueChanged.connect(lambda *_, k=k: self._abschluss_regler(k))
        for t, f in (("Tiefe:", self.d_tiefe_f), ("Größe der Tiefe:", self.d_tiefe), ("Kontur:", self.d_kontur_f), ("Größe der Kontur:", self.d_kontur),
                     ("Material:", self.d_material), ("Beleuchtung:", self.d_licht), ("Winkel:", self.d_winkel)):
            self.a_3d.zeile(t, f)
        self.a_3d.breit(zr3)
        seite.layout().replaceWidget(alt, self.a_3d); alt.hide(); alt.setParent(None); alt.deleteLater()
        self._ab_stumm = False
        return seite

    # ---- Oberer / Unterer Abschluss: Auswahl der Art (Bildchen), Breite und Höhe
    def _abschluss_menue(self, k: str) -> None:
        m = VoreinstellungMenue(self, keine=("Kein Abschluss", QIcon(BE.abschluss_symbol("keine"))), kachel=QSize(*GROESSE_ABSCHLUSS_KACHEL))
        m.abschnitt("Abschluss", [(a, QIcon(BE.abschluss_symbol(a)), n) for a, n in BEW.ABSCHLUSS], 3)
        m.gewaehlt.connect(lambda a: self._abschluss_setzen(k, a or "keine"))
        m.exec(self.ab_knopf[k].mapToGlobal(self.ab_knopf[k].rect().bottomLeft()))

    def _abschluss_setzen(self, k: str, art: str) -> None:
        self.ab_art[k] = art
        self.ab_knopf[k].setText("Keine" if art == "keine" else dict(BEW.ABSCHLUSS)[art])
        self._neu()

    def _abschluss_regler(self, k: str) -> None:
        """Wer Breite oder Höhe bewegt, schaltet den Abschluss ein (Rund), wenn er aus war."""
        if getattr(self, "_ab_stumm", True):
            return
        if self.ab_art[k] == "keine":
            self._abschluss_setzen(k, "rund")
        else:
            self._neu()

    def _setze_effekte(self, w: dict) -> None:
        super()._setze_effekte(w)
        if self.MIT_ABSCHLUSS:
            self._ab_stumm = True
            d3 = w.get("d3") or {}
            for k in ("oben", "unten"):
                ab = d3.get(k) or {}
                self.ab_art[k] = ab.get("art", "keine")
                self.ab_knopf[k].setText("Keine" if self.ab_art[k] == "keine" else dict(BEW.ABSCHLUSS).get(self.ab_art[k], "Eigene"))
                self.ab_breite[k].setValue(ab.get("breite", 4.0)); self.ab_hoehe[k].setValue(ab.get("hoehe", 6.0))
            self._ab_stumm = False

    def _werte_effekte(self) -> dict:
        fx = super()._werte_effekte()
        if self.MIT_ABSCHLUSS and any(a != "keine" for a in self.ab_art.values()):
            d3 = fx.get("d3") or {"tiefe": 0.0, "tiefe_farbe": self.d_tiefe_f.farbe or Farbe.GRAU, "kontur": 0.0, "kontur_farbe": self.d_kontur_f.farbe or Farbe.TINTE,
                                  "material": self._material, "beleuchtung": self._licht, "winkel": self.d_winkel.value()}
            for k, a in self.ab_art.items():
                if a != "keine":
                    d3[k] = {"art": a, "breite": self.ab_breite[k].value(), "hoehe": self.ab_hoehe[k].value()}
            fx["d3"] = d3
        return fx


class _TextPanel(_DreiDUntereinander, TexteffektPanel):
    """Die Textoptionen: das Panel der Texteffekte mit dem schmalen 3D-Format."""
