"""Effekte-Seite mit nur drei Abschnitten (Schatten, Leuchten, Weiche Kanten) — wie die Vorlage des Diagramms.

Mixin vor ``ObjektFormatPanel`` (Muster ``_DreiDUntereinander``: ruft ``super()``):
- ``_seite_effekte``: Reflektion, 3D-Format und 3D-Drehung werden ausgeblendet (ihre Regler und Daten bleiben und werden weiter geliefert);
  die Abschnitte stehen zugeklappt und klappen einzeln auf (``EinzelOffen``); der Schattenwinkel ist ein ``WinkelFeld`` (der ausgeblendete
  ``s_winkel`` bleibt Datenquelle und wird synchron gehalten).
- ``_teil_in_regler`` / ``_setze_effekte``: ohne gespeicherten Effekt zeigen die Regler Nullwerte (Schatten 0 %/0 %/0 pt/0 pt/0°, Leuchten 0 pt/0 %,
  Weiche Kanten 0 pt); gespeicherte Werte bleiben unverändert. Das ist nur Vorbelegung, es schaltet keinen Effekt ein.
- ``alle_zu()`` klappt alle Abschnitte zu (nach dem Setzen eines anderen Teils, falls gewünscht).
"""
from __future__ import annotations

from PySide6.QtWidgets import QLabel

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.abschnitt_gruppe import EinzelOffen
from lunivo_writer.ui.baukasten.winkel_feld import WinkelFeld


class NurDreiEffekteMixin:
    NUR_DREI_EFFEKTE = True                      # False in der Panelklasse schaltet das Mixin ab (SmartArt)

    def _seite_effekte(self, w: dict):
        seite = super()._seite_effekte(w)
        if not self.NUR_DREI_EFFEKTE:
            return seite
        for a in (self.a_refl, self.a_3d, self.a_dreh):
            a.hide()
        # Schattenwinkel: Drehknopf + Zähler statt Regler
        for l in self.a_schatten.inhalt.findChildren(QLabel):
            if l.buddy() is self.s_winkel:
                l.hide()
        self.s_winkel.hide()
        self.w_winkel = WinkelFeld(0.0, 360.0, "°", 1.0, 1, 0.0)
        self.a_schatten.zeile("Winkel", self.w_winkel)
        self.w_winkel.valueChanged.connect(lambda v: self.s_winkel.setValue(v, melden=True))
        self._effekt_gruppe = EinzelOffen(self.a_schatten, self.a_leucht, self.a_weich)
        for a in (self.a_schatten, self.a_leucht, self.a_weich):
            a.knopf.setChecked(False)
        return seite

    def alle_zu(self) -> None:
        if self.NUR_DREI_EFFEKTE:
            self._effekt_gruppe.schliesse_alle()

    def _teil_in_regler(self, name: str) -> None:
        if not self.NUR_DREI_EFFEKTE:
            super()._teil_in_regler(name)
            return
        if self._fx.get(name) is None and name in ("schatten", "leuchten"):
            if name == "schatten":
                self._fx_null_schatten()
            else:
                self.l_farbe.setFarbe(Farbe.BLAU); self.l_gross.setValue(0); self.l_trans.setValue(0)
        else:
            super()._teil_in_regler(name)
        if name == "schatten" and hasattr(self, "w_winkel"):
            self.w_winkel.setValue(self.s_winkel.value())

    def _fx_null_schatten(self) -> None:
        self.s_farbe.setFarbe(Farbe.SCHWARZ); self.s_trans.setValue(0); self.s_gross.setValue(0)
        self.s_weich.setValue(0); self.s_abst.setValue(0); self.s_winkel.setValue(0)

    def _setze_effekte(self, w: dict) -> None:
        super()._setze_effekte(w)
        if self.NUR_DREI_EFFEKTE and not w.get("weich"):
            self.w_radius.setValue(0)
