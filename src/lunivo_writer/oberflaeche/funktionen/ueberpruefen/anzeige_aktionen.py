"""Aktion der Anzeige zur Überprüfung: Endgültige Version mit/ohne Markup oder Original. Die Befehle liegen im Farmwork."""
from __future__ import annotations


class AnzeigeAktionen:
    def _anzeige_index(self) -> int:
        return self._anzeige().index()

    def ueberpruefenAnzeige(self, k=None, index: int = 0):
        """Was das Dokumentfenster zeigt: mit oder ohne Markup, oder das Original ohne die verfolgten Änderungen (schreibgeschützt)."""
        if self.w.current_tab() is None:
            return
        self._anzeige().setzen(index)
