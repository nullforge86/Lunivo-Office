"""Anschluss der Bedienelemente „Ansicht“ an das Farmwork: liefert die Befehle des Farmworks für den aktuellen Editor und leitet dessen Meldungen in die
Statusleiste. ``self.w`` ist das Hauptfenster, ``self.ed`` der Editor."""
from __future__ import annotations

from framework.schnittstellen.datentypen.ereignisdaten import Art, Ereignis
from framework.befehle.ansicht.befehle import AnsichtBefehle
from framework.ereignisse.ereignissteuerung import Melder


class AnsichtAnschluss:
    def _ansicht(self) -> AnsichtBefehle | None:
        """Die Befehle des Farmworks für den aktuellen Editor (``None`` ohne Dokument)."""
        if self.ed is None:
            return None
        if getattr(self, "_an_melder", None) is None:
            self._an_melder = Melder()
            self._an_melder.abonnieren(Art.MELDUNG, self._an_meldung)
        return AnsichtBefehle(self.ed, self._an_melder)

    def _an_meldung(self, e: Ereignis) -> None:
        self.w.statusBar().showMessage(e.text, e.daten.get("dauer_ms", 4000))
