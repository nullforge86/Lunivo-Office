"""Orte des Benutzers für Programmdaten, Zwischenspeicher, Einstellungen, nachgeladene Schriften und Vorlagen – je Betriebssystem erkannt.

Direkt über Umgebungsvariablen, ohne Qt:

* Linux: XDG Base Directory – ``$XDG_DATA_HOME`` (Standard ``~/.local/share``), ``$XDG_CACHE_HOME`` (Standard ``~/.cache``),
  ``$XDG_CONFIG_HOME`` (Standard ``~/.config``). Dieselben Orte wie bisher; nichts wird verschoben oder gelöscht.
* Windows: ``%APPDATA%`` (Daten und Einstellungen), ``%LOCALAPPDATA%`` (Zwischenspeicher).
* macOS: ``~/Library/Application Support`` (Daten und Einstellungen), ``~/Library/Caches`` (Zwischenspeicher).
"""
from __future__ import annotations

import os
import sys

ORGANISATION = "Lunivo"
PROGRAMM = "Lunivo Writer"


def _heim() -> str:
    return os.path.expanduser("~")


def _umgebung(variable: str, vorgabe: str) -> str:
    """Absoluter Pfad aus der Umgebungsvariablen, sonst ``vorgabe`` unter dem Benutzerordner."""
    wert = os.environ.get(variable, "")
    return wert if wert and os.path.isabs(wert) else os.path.join(_heim(), vorgabe)


def daten_basis() -> str:
    """Grundordner für Benutzerdaten: Linux ``$XDG_DATA_HOME``, Windows ``%APPDATA%``, macOS ``~/Library/Application Support``."""
    if sys.platform == "win32":
        return _umgebung("APPDATA", os.path.join("AppData", "Roaming"))
    if sys.platform == "darwin":
        return os.path.join(_heim(), "Library", "Application Support")
    return _umgebung("XDG_DATA_HOME", os.path.join(".local", "share"))


def cache_basis() -> str:
    """Grundordner für Zwischengelagertes: Linux ``$XDG_CACHE_HOME``, Windows ``%LOCALAPPDATA%``, macOS ``~/Library/Caches``."""
    if sys.platform == "win32":
        return _umgebung("LOCALAPPDATA", os.path.join("AppData", "Local"))
    if sys.platform == "darwin":
        return os.path.join(_heim(), "Library", "Caches")
    return _umgebung("XDG_CACHE_HOME", ".cache")


def config_basis() -> str:
    """Grundordner für Einstellungen: Linux ``$XDG_CONFIG_HOME``, Windows und macOS wie ``daten_basis``."""
    if sys.platform in ("win32", "darwin"):
        return daten_basis()
    return _umgebung("XDG_CONFIG_HOME", ".config")


def data_dir() -> str:
    """Programmdaten des Benutzers (gelernte Wörter, Sicherungen, KI-Einstellungen …); wird bei Bedarf angelegt."""
    base = os.path.join(daten_basis(), ORGANISATION, PROGRAMM)
    os.makedirs(base, exist_ok=True)
    return base


def cache_dir() -> str:
    """Wiederherstellbares Zwischengelagertes."""
    base = os.path.join(cache_basis(), ORGANISATION, PROGRAMM)
    os.makedirs(base, exist_ok=True)
    return base


def config_dir() -> str:
    """Ordner der Einstellungsdatei (Linux: ``$XDG_CONFIG_HOME/lunivo``); wird bei Bedarf angelegt."""
    base = os.path.join(config_basis(), "lunivo")
    os.makedirs(base, exist_ok=True)
    return base


def schriften_dir() -> str:
    """Nachgeladene Lese-Schriften (schrift-holen.sh); Linux: ~/.local/share/fonts/lunivo-office."""
    return os.path.join(daten_basis(), "fonts", "lunivo-office")


def vorlagen_dir() -> str:
    """Vorgabeordner eigener Vorlagen, wenn der Benutzer keinen eigenen gewählt hat."""
    return os.path.join(_heim(), "Vorlagen")
