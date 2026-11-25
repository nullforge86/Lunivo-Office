"""Kleine Worker-Hüllen für asynchrone KI-Aufträge."""
from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, Signal


class _Sig(QObject):
    fertig = Signal(object, object)
    teil = Signal(int, str)


class _Lauf(QRunnable):
    def __init__(self, auftrag, arbeit, sig):
        super().__init__()
        self.auftrag, self.arbeit, self.sig = auftrag, arbeit, sig

    def run(self):
        try:
            r = self.arbeit()
        except Exception as e:
            r = {"fehler": f"Es hat nicht geklappt: {e}"}
        try:
            self.sig.fertig.emit(self.auftrag, r)
        except RuntimeError:
            pass                                      # Empfänger wurde beim Schließen bereits freigegeben
