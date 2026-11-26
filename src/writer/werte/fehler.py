"""Fehler, die die Oberfläche gemeldet bekommt: eigene Typen dieser Schicht (Fehler des Kerns und des Frameworks werden vorher gefangen und übersetzt)."""
from __future__ import annotations


class Dateifehler(Exception):
    """Datei nicht lesbar oder nicht schreibbar — der Text ist für Anwender gedacht."""


class Bildfehler(ValueError):
    """Bilddatei nicht verwendbar; die Meldung ist für den Benutzer."""


class KennwortNoetig(Dateifehler):
    """Das Dokument ist verschlüsselt; ohne (richtiges) Kennwort lässt es sich nicht öffnen. ``falsch``: ein Kennwort war angegeben, stimmt aber nicht."""

    def __init__(self, falsch: bool = False):
        super().__init__("Das Kennwort ist falsch." if falsch else "Das Dokument ist durch ein Kennwort geschützt.")
        self.falsch = falsch
