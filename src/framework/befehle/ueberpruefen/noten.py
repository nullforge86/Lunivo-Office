"""Befehle der Fuß- und Endnoten: neue Note anlegen und Noten durchgehen – für das Dokument mit der Kennung."""
from __future__ import annotations

from framework.befehle import ausfuehren, im_kontext_bewegen


class NotenBefehle:
    def __init__(self, kennung: int):
        self._kennung = kennung

    def neu(self, art: str) -> int:
        """Setzt das Zeichen der Note in den Text; gibt die Nummer der Note zurück (die Oberfläche öffnet damit das Notenfeld), 0 wenn es nicht geht."""
        return ausfuehren(self._kennung, lambda s: s.note_einfuegen("", art)) or 0

    def springen(self, delta: int, art: str | None = None) -> None:
        im_kontext_bewegen(self._kennung, lambda k: int(k.springe([n for n in k.noten_stellen() if art is None or n["art"] == art], delta) is not None))
