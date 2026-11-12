"""Orte für Programmdaten, Zwischenspeicher, nachgeladene Schriften/Stimmen und Vorlagen (über QStandardPaths).

Unter Linux liegen sie an denselben Stellen wie bisher (~/.local/share/…), unter Windows und macOS an den dort üblichen.
Nichts wird verschoben oder gelöscht; die älteren Linux-Orte der Stimmen bleiben als Suchort erhalten.
"""
from __future__ import annotations

import os

from PySide6.QtCore import QStandardPaths

_SP = QStandardPaths


def _ort(art) -> str:
    return _SP.writableLocation(art)


def data_dir() -> str:
    """Programmdaten des Benutzers (gelernte Wörter, Sicherungen, KI-Einstellungen …); wird bei Bedarf angelegt."""
    base = _ort(_SP.AppDataLocation)
    os.makedirs(base, exist_ok=True)
    return base


def cache_dir() -> str:
    """Wiederherstellbares Zwischengelagertes."""
    base = _ort(_SP.CacheLocation)
    os.makedirs(base, exist_ok=True)
    return base


def schriften_dir() -> str:
    """Nachgeladene Lese-Schriften (schrift-holen.sh); Linux: ~/.local/share/fonts/lunivo-office."""
    return os.path.join(_ort(_SP.GenericDataLocation), "fonts", "lunivo-office")


def piper_dirs() -> list[str]:
    """Suchorte für Piper und seine Stimmen (stimme-holen.sh), der erste ist der aktuelle."""
    generisch = _ort(_SP.GenericDataLocation)
    return [os.path.join(generisch, "lunivo-office", "piper"), os.path.join(generisch, "schreibhilfe", "piper")]


def argos_dirs() -> list[str]:
    """Suchorte für Argos-Sprachpakete (.argosmodel): Benutzerordner zuerst, dann der mitgelieferte Ordner beim Programm."""
    generisch = _ort(_SP.GenericDataLocation)
    programm = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "argos"))
    return [os.path.join(generisch, "lunivo-office", "argos"), programm, "/opt/stevie-empire/lunivo-office/argos"]


def argos_pakete_dir() -> str:
    """Beschreibbarer Ort, an dem Argos die installierten Sprachpakete ablegt (der mitgelieferte Ordner ist schreibgeschützt)."""
    pfad = os.path.join(data_dir(), "argos-pakete")
    os.makedirs(pfad, exist_ok=True)
    return pfad


def vorlagen_dir() -> str:
    """Vorgabeordner eigener Vorlagen, wenn der Benutzer keinen eigenen gewählt hat."""
    return os.path.join(_ort(_SP.HomeLocation), "Vorlagen")
