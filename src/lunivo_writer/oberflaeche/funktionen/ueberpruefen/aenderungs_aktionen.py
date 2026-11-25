"""Aktionen und Zustände der Änderungs-Knöpfe im Reiter „Überprüfen“: verfolgen, Markup, durchgehen, annehmen, ablehnen. Die Befehle liegen im Farmwork."""
from __future__ import annotations


class AenderungsAktionen:
    def verfolgen(self, k=None):
        fw = self._aenderungen()
        if fw is not None:
            fw.verfolgen_umschalten(self._schutz_wert())

    def an_verfolgen(self):
        fw = self._aenderungen()
        return bool(fw is not None and fw.verfolgt())

    def markupUmschalten(self, k=None):
        fw = self._aenderungen()
        if fw is not None:
            fw.markup_umschalten()

    def an_markupUmschalten(self):
        fw = self._aenderungen()
        return bool(fw is not None and fw.markup_an())

    def ueberarbeitungsbereich(self, k=None): self.w.zeige_navigation("aenderungen")

    def aenderungAnnehmen(self, k=None): self._aend_am_cursor(True)

    def aenderungAblehnen(self, k=None): self._aend_am_cursor(False)

    def _aend_am_cursor(self, annehmen):
        fw = self._aenderungen()
        if fw is not None:
            fw.am_zeiger_entscheiden(annehmen, self._schutz_wert())

    def aenderungWeiter(self, k=None):
        fw = self._aenderungen()
        if fw is not None:
            fw.springen(1)

    def aenderungZurueck(self, k=None):
        fw = self._aenderungen()
        if fw is not None:
            fw.springen(-1)

    def aenderungenUebernehmen(self, k=None):
        fw = self._aenderungen()
        if fw is not None:
            fw.alle_entscheiden(True, self._schutz_wert())

    def aenderungenVerwerfen(self, k=None):
        fw = self._aenderungen()
        if fw is not None:
            fw.alle_entscheiden(False, self._schutz_wert())
