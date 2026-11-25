"""Setzt den ``VorschauPort`` des Farmworks mit der Vorschau-Ansicht des Dokumentfensters um (Original ohne Markup, Seriendruck-Vorschau)."""
from __future__ import annotations

from lunivo_writer.oberflaeche.dokument.ansicht import vorschau_ansicht


class VorschauAdapter:
    def __init__(self, tab):
        self._tab = tab

    def zeigen(self, dokument: object, art: str) -> None:
        vorschau_ansicht.zeigen(self._tab, dokument, art)

    def aktiv(self, art: str) -> bool:
        return self._tab is not None and bool(vorschau_ansicht.aktiv(self._tab, art))

    def beenden(self) -> None:
        vorschau_ansicht.beenden(self._tab)
