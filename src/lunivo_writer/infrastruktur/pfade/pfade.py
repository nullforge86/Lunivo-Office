"""Orte für Programmdaten, Zwischenspeicher, nachgeladene Schriften/Stimmen und Vorlagen nach XDG Base Directory.

Direkt über Umgebungsvariablen, ohne Qt: ``$XDG_DATA_HOME`` (Standard ``~/.local/share``), ``$XDG_CACHE_HOME`` (Standard ``~/.cache``),
``$XDG_CONFIG_HOME`` (Standard ``~/.config``). Die Orte sind dieselben, die zuvor ``QStandardPaths`` unter Linux geliefert hat; nichts wird
verschoben oder gelöscht, die älteren Orte der Stimmen bleiben als Suchort erhalten.
"""
from __future__ import annotations

import os

ORGANISATION = "Lunivo"
PROGRAMM = "Lunivo Writer"


def _heim() -> str:
    return os.path.expanduser("~")


def _xdg(variable: str, vorgabe: str) -> str:
    wert = os.environ.get(variable, "")
    return wert if wert and os.path.isabs(wert) else os.path.join(_heim(), vorgabe)


def daten_basis() -> str:
    """``$XDG_DATA_HOME`` (Standard ``~/.local/share``)."""
    return _xdg("XDG_DATA_HOME", os.path.join(".local", "share"))


def cache_basis() -> str:
    """``$XDG_CACHE_HOME`` (Standard ``~/.cache``)."""
    return _xdg("XDG_CACHE_HOME", ".cache")


def config_basis() -> str:
    """``$XDG_CONFIG_HOME`` (Standard ``~/.config``)."""
    return _xdg("XDG_CONFIG_HOME", ".config")


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
    """Ordner der Einstellungsdatei: ``$XDG_CONFIG_HOME/lunivo``; wird bei Bedarf angelegt."""
    base = os.path.join(config_basis(), "lunivo")
    os.makedirs(base, exist_ok=True)
    return base


def schriften_dir() -> str:
    """Nachgeladene Lese-Schriften (schrift-holen.sh); Linux: ~/.local/share/fonts/lunivo-office."""
    return os.path.join(daten_basis(), "fonts", "lunivo-office")


def piper_dirs() -> list[str]:
    """Suchorte für Piper und seine Stimmen (stimme-holen.sh), der erste ist der aktuelle."""
    generisch = daten_basis()
    return [os.path.join(generisch, "lunivo-office", "piper"), os.path.join(generisch, "schreibhilfe", "piper")]


def argos_dirs() -> list[str]:
    """Suchorte für Argos-Sprachpakete (.argosmodel): Benutzerordner zuerst, dann der mitgelieferte Ordner beim Programm."""
    programm = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "argos"))
    return [os.path.join(daten_basis(), "lunivo-office", "argos"), programm, "/opt/stevie-empire/lunivo-office/argos"]


def argos_pakete_dir() -> str:
    """Beschreibbarer Ort, an dem Argos die installierten Sprachpakete ablegt (der mitgelieferte Ordner ist schreibgeschützt)."""
    pfad = os.path.join(data_dir(), "argos-pakete")
    os.makedirs(pfad, exist_ok=True)
    return pfad


def vorlagen_dir() -> str:
    """Vorgabeordner eigener Vorlagen, wenn der Benutzer keinen eigenen gewählt hat."""
    return os.path.join(_heim(), "Vorlagen")
