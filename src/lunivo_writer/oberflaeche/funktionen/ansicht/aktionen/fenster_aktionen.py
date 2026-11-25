"""Aktionen der Fenster-Knöpfe in der Ansicht: neues Fenster, Fenster anordnen, Fensterliste."""
from __future__ import annotations


class FensterAktionen:
    def neuesFenster(self, k=None): self.w.neues_fenster()

    def fensterNebeneinander(self, k=None): self.w.fenster_anordnen("nebeneinander")

    def fensterUntereinander(self, k=None): self.w.fenster_anordnen("untereinander")

    def fensterKacheln(self, k=None): self.w.fenster_anordnen("kacheln")

    def fensterListe(self, k=None):
        self._popup(self.w.fensterliste_menue())
