"""Bei „Automatische Füllung“ / „Automatische Linie“ die Felder zeigen, aber grau (nicht bedienbar), wie in der Vorlage.

Mixin vor ``ObjektFormatPanel``: ruft erst die Basis (``_felder_zeigen``) und blendet dann bei Automatisch die Gruppen
``g_farbe`` (Farbe, Transparenz) bzw. ``g_lin_form`` (Farbe, Transparenz, Breite, Kombinierter Typ, Strichtyp, Abschluss, Verknüpfung,
Anfangs-/Endpfeil, Abgerundete Ecke) ein und deaktiviert sie (die Pfeile sind zusätzlich nur bei Linienreihen frei).
Mit ``AUTO_FELDER = False`` in der Panelklasse ist das Verhalten abgeschaltet.
"""
from __future__ import annotations


class AutoFelderMixin:
    AUTO_FELDER = False                                  # keine grauen, nicht bedienbaren Felder: bei „Automatisch“ erscheinen sie erst mit der Füllungs-/Linienart, die sie brauchen

    def _felder_zeigen(self) -> None:
        super()._felder_zeigen()
        if not hasattr(self, "g_lin_form"):
            return
        if hasattr(self, "l_farbe_text"):                      # die Beschriftung folgt dem Farbfeld (bei Farbverlauf entfällt es)
            self.l_farbe_text.setVisible(not self.k_farbe.isHidden())
        if not self.AUTO_FELDER:
            return
        r_auto, k_auto = getattr(self, "r_auto", None), getattr(self, "k_auto", None)
        fuell = r_auto is not None and r_auto.isChecked()
        linie = k_auto is not None and k_auto.isChecked()
        self._auto_gruppe((self.g_farbe,), fuell)
        self._auto_gruppe((self.g_lin_form,), linie)

    @staticmethod
    def _auto_gruppe(gruppen, auto: bool) -> None:
        for g in gruppen:
            if g is None:
                continue
            if auto:
                g.setVisible(True)
            g.setEnabled(not auto)
