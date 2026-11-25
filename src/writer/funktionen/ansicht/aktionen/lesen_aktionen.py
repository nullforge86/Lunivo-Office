"""Aktionen der Lesehilfen in der Ansicht: Text ausblenden und Silben farbig anzeigen. Schalter und Befehle liegen im Farmwork."""
from __future__ import annotations

from framework.funktionen.ansicht import lesehilfe


class LesenAktionen:
    def ausblenden(self, k=None):
        """Markierten Text als „ausgeblendet“ formatieren (Strg+Umschalt+H)."""
        fw = self._ansicht()
        if fw is not None:
            fw.ausblenden_umschalten()

    def an_ausblenden(self):
        fw = self._ansicht()
        return bool(fw is not None and fw.ausgeblendet())

    def silbenfarben(self, k=None):
        an = lesehilfe.silben_umschalten(self.w.settings)
        self.w.silbenfarben_anwenden()
        self.w.statusBar().showMessage("Silben werden farbig angezeigt." if an else "Silbenfarben aus.", 4000)

    def an_silbenfarben(self):
        return lesehilfe.silben_an(self.w.settings)
