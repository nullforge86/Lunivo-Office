"""Anschluss der Bedienelemente „Bearbeiten“ an das Farmwork: liefert die Befehle des Farmworks für den aktuellen Editor und leitet Meldungen in die Statusleiste.
``self.w`` ist das Hauptfenster, ``self.ed`` der Editor."""
from __future__ import annotations

from lunivo_writer.farmwork.datentypen.ereignisdaten import Art, Ereignis
from lunivo_writer.farmwork.funktionen.bearbeiten.befehle import BearbeitenBefehle
from lunivo_writer.farmwork.steuerung.ereignissteuerung import Melder


class BearbeitenAnschluss:
    def _bearbeiten(self) -> BearbeitenBefehle | None:
        """Die Befehle des Farmworks für den aktuellen Editor (``None`` ohne Dokument)."""
        if self.ed is None:
            return None
        if getattr(self, "_be_melder", None) is None:
            self._be_melder = Melder()
            self._be_melder.abonnieren(Art.MELDUNG, self._be_meldung)
        return BearbeitenBefehle(self.ed, self._be_melder)

    def _be_meldung(self, e: Ereignis) -> None:
        self.w.statusBar().showMessage(e.text, e.daten.get("dauer_ms", 4000))
