"""Anschluss der Bedienelemente „Überprüfen“ an das Farmwork: liefert die Befehle des Farmworks für den aktuellen Editor, verbindet deren Meldungen mit der
Statusleiste und kennt den Dokumentschutz des Dokumentfensters. ``self.w`` ist das Hauptfenster, ``self.ed`` der Editor."""
from __future__ import annotations

from writer.ueberpruefung.befehle import (SCHUTZ_HINWEIS, aenderungen_befehle, anzeige_befehle, ist_geschuetzt, kommentare_befehle, markup_befehle,
                                         meldungen_an, noten_befehle)
from vcl.qt.widgets.ribbon.ueberpruefen.band.vorschau_adapter import VorschauAdapter


class UeberpruefenAnschluss:
    @staticmethod
    def _sym(name):
        """Das Symbol eines Menüeintrags (auch von anderen Bausteinen der Befehle genutzt)."""
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        return symbole.icon(name, 18)

    def _markup(self):
        return markup_befehle(self.ed.kennung, self.w.settings, self._ue_melder()) if self.ed is not None else None

    def _anzeige(self):
        return anzeige_befehle(self.ed.kennung if self.ed is not None else None, VorschauAdapter(self.w.current_tab()))

    def _ue_melder(self):
        if getattr(self, "_ue_melder_objekt", None) is None:
            self._ue_melder_objekt = meldungen_an(self._ue_meldung)
        return self._ue_melder_objekt

    def _ue_meldung(self, text: str, dauer_ms: int) -> None:
        self.w.statusBar().showMessage(text, dauer_ms)

    def _kommentare(self):
        return kommentare_befehle(self.ed.kennung, self._ue_melder()) if self.ed is not None else None

    def _aenderungen(self):
        return aenderungen_befehle(self.ed.kennung, self._ue_melder()) if self.ed is not None else None

    def _noten(self):
        return noten_befehle(self.ed.kennung) if self.ed is not None else None

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
