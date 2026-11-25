"""Anzeige zur Überprüfung: mit oder ohne Markup, oder das Original ohne die verfolgten Änderungen (schreibgeschützt)."""
from __future__ import annotations

from core.funktionen.ueberpruefen import fassungen
from framework.schnittstellen.dokument import EditorPort
from framework.schnittstellen.vorschau import VorschauPort

ANZEIGEN = ("Endgültige Version enthält Markups", "Endgültige Version", "Original enthält Markups", "Original")
ORIGINAL = 3


class AnzeigeBefehle:
    def __init__(self, editor: EditorPort | None, vorschau: VorschauPort):
        self._e = editor
        self._vorschau = vorschau

    def index(self) -> int:
        """Welche Anzeige gerade gilt (Index in ``ANZEIGEN``)."""
        if self._vorschau.aktiv("original"):
            return ORIGINAL
        return 0 if (self._e is None or self._e.markup) else 1

    def setzen(self, index: int) -> None:
        """Was das Dokumentfenster zeigt: mit oder ohne Markup, oder das Original ohne die verfolgten Änderungen."""
        if self._e is None:
            return
        if index == ORIGINAL:
            self._vorschau.zeigen(fassungen.original(self._e.sitzung.dokument), "original")
            return
        if self._vorschau.aktiv("original"):
            self._vorschau.beenden()
        self._e.set_markup(index != 1)
