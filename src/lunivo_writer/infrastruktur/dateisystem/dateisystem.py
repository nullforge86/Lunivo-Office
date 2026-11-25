"""Dateisystem-Besonderheiten der Betriebssysteme an einer Stelle (heute: wie eine Datei für ``fsync`` geöffnet werden muss)."""
from __future__ import annotations

import os
import sys


def fsync_oeffnen(path: str) -> int:
    """Dateikennung für ``os.fsync``. Windows braucht dafür einen schreibenden Zugriff, Linux und macOS genügt Lesen."""
    return os.open(path, os.O_RDWR if os.name == "nt" else os.O_RDONLY)


def ordner_oeffnen(ordner: str) -> int:
    """Kennung eines Ordners zum ``fsync`` (sichert das Umbenennen); wirft OSError, wo das Betriebssystem es nicht kann (Windows)."""
    return os.open(ordner, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))


def datenordner() -> str:
    """Datenordner des Programms für Benutzerdaten wie Sicherungen, ohne Qt: dieselbe Stelle wie ``QStandardPaths.AppDataLocation`` für die Organisation
    „Lunivo“ und das Programm „Lunivo Writer“ (Linux: ``~/.local/share``, Windows: ``%APPDATA%``, macOS: ``~/Library/Application Support``). Wird bei Bedarf angelegt."""
    heim = os.path.expanduser("~")
    if sys.platform == "win32":
        basis = os.environ.get("APPDATA") or os.path.join(heim, "AppData", "Roaming")
    elif sys.platform == "darwin":
        basis = os.path.join(heim, "Library", "Application Support")
    else:
        basis = os.environ.get("XDG_DATA_HOME") or os.path.join(heim, ".local", "share")
    pfad = os.path.join(basis, "Lunivo", "Lunivo Writer")
    os.makedirs(pfad, exist_ok=True)
    return pfad
