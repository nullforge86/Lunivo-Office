"""Anzeige zur Überprüfung: mit oder ohne Markup, oder das Original ohne die verfolgten Änderungen (schreibgeschützt)."""
from __future__ import annotations

from core.aenderungsverfolgung.vergleich import fassungen
from framework.befehle import lesen
from framework.schnittstellen.vorschau import VorschauPort
from framework.sitzungen import sitzung as _steuerung

ANZEIGEN = ("Endgültige Version enthält Markups", "Endgültige Version", "Original enthält Markups", "Original")
ORIGINAL = 3


class AnzeigeBefehle:
    def __init__(self, kennung: int | None, vorschau: VorschauPort):
        self._kennung = kennung
        self._vorschau = vorschau

    def index(self) -> int:
        """Welche Anzeige gerade gilt (Index in ``ANZEIGEN``)."""
        if self._vorschau.aktiv("original"):
            return ORIGINAL
        return 0 if (self._kennung is None or _steuerung.markup_an(self._kennung)) else 1

    def setzen(self, index: int) -> None:
        """Was das Dokumentfenster zeigt: mit oder ohne Markup, oder das Original ohne die verfolgten Änderungen."""
        if self._kennung is None:
            return
        if index == ORIGINAL:
            original = lesen(self._kennung, lambda s: fassungen.original(s.dokument))
            if original is not None:
                self._vorschau.zeigen(original, "original")
            return
        if self._vorschau.aktiv("original"):
            self._vorschau.beenden()
        _steuerung.markup_setzen(self._kennung, index != 1)
