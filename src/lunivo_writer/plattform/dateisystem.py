"""Dateisystem-Besonderheiten der Betriebssysteme an einer Stelle (heute: wie eine Datei für ``fsync`` geöffnet werden muss)."""
from __future__ import annotations

import os


def fsync_oeffnen(path: str) -> int:
    """Dateikennung für ``os.fsync``. Windows braucht dafür einen schreibenden Zugriff, Linux und macOS genügt Lesen."""
    return os.open(path, os.O_RDWR if os.name == "nt" else os.O_RDONLY)


def ordner_oeffnen(ordner: str) -> int:
    """Kennung eines Ordners zum ``fsync`` (sichert das Umbenennen); wirft OSError, wo das Betriebssystem es nicht kann (Windows)."""
    return os.open(ordner, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
