"""Aktionen der Noten-Knöpfe: Fuß- und Endnote einfügen, durchgehen, Notenfeld öffnen. Die Befehle liegen im Farmwork."""
from __future__ import annotations


class NotenAktionen:
    def _note(self, art, titel):
        """Neue Note: das Zeichen kommt in den Text, unten öffnet sich das Notenfeld mit dem Cursor darin."""
        fw = self._noten()
        if fw is not None:
            self.w.noten_feld.oeffnen(art, fw.neu(art))

    def fussnote(self, k=None): self._note("f", "Fußnote einfügen")

    def endnote(self, k=None): self._note("e", "Endnote einfügen")

    def noteWeiter(self, k=None):
        fw = self._noten()
        if fw is not None:
            fw.springen(1)

    def noteZurueck(self, k=None):
        fw = self._noten()
        if fw is not None:
            fw.springen(-1)

    def notenZeigen(self, k=None): self.w.zeige_navigation("noten")

    def note_bearbeiten(self, art, nid):
        if self.ed:
            self.w.noten_feld.oeffnen(art, nid)
