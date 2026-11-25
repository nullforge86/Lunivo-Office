"""Anschluss der Bedienelemente „Überprüfen“ an das Farmwork: liefert die Befehle des Farmworks für den aktuellen Editor, verbindet deren Meldungen mit der
Statusleiste und kennt den Dokumentschutz des Dokumentfensters. ``self.w`` ist das Hauptfenster, ``self.ed`` der Editor."""
from __future__ import annotations

from lunivo_writer.farmwork.datentypen.ereignisdaten import Art, Ereignis
from lunivo_writer.farmwork.funktionen.ueberpruefen.aenderungen import AenderungenBefehle
from lunivo_writer.farmwork.funktionen.ueberpruefen.anzeige import AnzeigeBefehle
from lunivo_writer.farmwork.funktionen.ueberpruefen.kommentare import KommentareBefehle
from lunivo_writer.farmwork.funktionen.ueberpruefen.markup import MarkupBefehle
from lunivo_writer.farmwork.funktionen.ueberpruefen.noten import NotenBefehle
from lunivo_writer.farmwork.funktionen.ueberpruefen.schutz import SCHUTZ_HINWEIS, ist_geschuetzt
from lunivo_writer.farmwork.steuerung.ereignissteuerung import Melder
from lunivo_writer.oberflaeche.funktionen.ueberpruefen.band.vorschau_adapter import VorschauAdapter


class UeberpruefenAnschluss:
    @staticmethod
    def _sym(name):
        """Das Symbol eines Menüeintrags (auch von anderen Bausteinen der Befehle genutzt)."""
        from lunivo_writer.oberflaeche.bauteile import symbole
        return symbole.icon(name, 18)

    def _markup(self) -> MarkupBefehle | None:
        return MarkupBefehle(self.ed, self.w.settings, self._ue_melder()) if self.ed is not None else None

    def _anzeige(self) -> AnzeigeBefehle:
        return AnzeigeBefehle(self.ed, VorschauAdapter(self.w.current_tab()))

    def _ue_melder(self) -> Melder:
        if getattr(self, "_ue_melder_objekt", None) is None:
            self._ue_melder_objekt = Melder()
            self._ue_melder_objekt.abonnieren(Art.MELDUNG, self._ue_meldung)
        return self._ue_melder_objekt

    def _ue_meldung(self, e: Ereignis) -> None:
        self.w.statusBar().showMessage(e.text, e.daten.get("dauer_ms", 4000))

    def _kommentare(self) -> KommentareBefehle | None:
        return KommentareBefehle(self.ed, self._ue_melder()) if self.ed is not None else None

    def _aenderungen(self) -> AenderungenBefehle | None:
        return AenderungenBefehle(self.ed, self._ue_melder()) if self.ed is not None else None

    def _noten(self) -> NotenBefehle | None:
        return NotenBefehle(self.ed) if self.ed is not None else None

    def _schutz_wert(self) -> str | None:
        """Der Dokumentschutz des aktuellen Dokumentfensters (``None``, ``lesen``, ``aenderungen``, ``kommentare``)."""
        t = self.w.current_tab()
        return getattr(t, "schutz", None) if t else None

    def _geschuetzt(self, *arten) -> bool:
        """Steht ein Dokumentschutz dieser Art (Überprüfen ▸ Bearbeitung einschränken), Hinweis in der Statusleiste und True."""
        if ist_geschuetzt(self._schutz_wert(), *arten):
            self.w.statusBar().showMessage(SCHUTZ_HINWEIS, 4000)
            return True
        return False
