"""Anschluss der Bedienelemente an das Framework: liefert die Befehle des Frameworks für den aktuellen Editor und verbindet dessen Ereignisse mit dem Fenster.

Gemeinsame Grundlage der übrigen Bausteine dieser Funktion; ``self.w`` ist das Hauptfenster, ``self.ed`` der Editor."""
from __future__ import annotations

from lunivo_writer.farmwork.schnittstellen.seiten_port import SeitenPort
from lunivo_writer.farmwork.datentypen.ereignisdaten import Art
from lunivo_writer.farmwork.steuerung.ereignissteuerung import Melder
from lunivo_writer.farmwork.funktionen.kopffuss.befehle import KopfFussBefehle


class KopfFussAnschluss:
    def _fw(self) -> KopfFussBefehle | None:
        """Die Befehle des Frameworks für den aktuellen Editor (``None`` ohne Dokument); die Ereignisse landen in diesem Fenster."""
        editor: SeitenPort | None = self.ed
        if editor is None:
            return None
        if getattr(self, "_kf_melder", None) is None:
            self._kf_melder = Melder()
            self._kf_melder.abonnieren(Art.MELDUNG, self._kf_meldung)
            self._kf_melder.abonnieren(Art.OEFFNEN, self._kf_oeffnen)
        return KopfFussBefehle(editor, self._kf_melder)

    def _kf_aktion(self, aktion: str) -> None:
        fw = self._fw()
        if fw is not None:
            fw.ausfuehren(aktion)
