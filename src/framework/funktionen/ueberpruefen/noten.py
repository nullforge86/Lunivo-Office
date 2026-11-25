"""Befehle der Fuß- und Endnoten: neue Note anlegen und Noten durchgehen. Der Editor kommt über den ``EditorPort`` herein."""
from __future__ import annotations

from framework.schnittstellen.dokument import EditorPort


class NotenBefehle:
    def __init__(self, editor: EditorPort):
        self._editor = editor

    def neu(self, art: str) -> int:
        """Setzt das Zeichen der Note in den Text; gibt die Nummer der Note zurück (die Oberfläche öffnet damit das Notenfeld)."""
        return self._editor.note_neu(art, "")

    def springen(self, delta: int) -> None:
        self._editor.note_springen(delta)
