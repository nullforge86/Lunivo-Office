"""Anschluss der Bedienelemente „Verweise“ an das Farmwork: liefert die Befehle des Farmworks für den aktuellen Editor und verbindet dessen Meldungen mit
dem Fenster. ``self.w`` ist das Hauptfenster, ``self.ed`` der Editor."""
from __future__ import annotations

from lunivo_writer.farmwork.datentypen.ereignisdaten import Art, Ereignis
from lunivo_writer.farmwork.funktionen.verweise.befehle import VerweiseBefehle
from lunivo_writer.farmwork.schnittstellen.dokument import EditorPort
from lunivo_writer.farmwork.steuerung.ereignissteuerung import Melder


class VerweiseAnschluss:
    def _vw(self) -> VerweiseBefehle | None:
        """Die Befehle des Farmworks für den aktuellen Editor (``None`` ohne Dokument)."""
        editor: EditorPort | None = self.ed
        if editor is None:
            return None
        if getattr(self, "_vw_melder", None) is None:
            self._vw_melder = Melder()
            self._vw_melder.abonnieren(Art.MELDUNG, self._vw_meldung)
        return VerweiseBefehle(editor, self.w.settings, self._vw_melder)

    def _vw_meldung(self, e: Ereignis) -> None:
        self.w.statusBar().showMessage(e.text, e.daten.get("dauer_ms", 4000))
