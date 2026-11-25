"""Aktionen zum Suchen: Suchen und Ersetzen im Feld der linken Seitenleiste."""
from __future__ import annotations


class SuchAktionen:
    def suchen(self, k=None, *_):
        self.w.find_dialog_show()

    def ersetzen(self, k=None, *_):
        self.w.find_dialog_show("Ersetzen")

    w_sucheZeigen = suchen
