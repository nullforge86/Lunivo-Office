"""Zusatzpakete (Offline-Übersetzung, Stimmen, Lese-Schriften): Suchorte und Erkennung an einer Stelle.

Ein Zusatzpaket wird an drei Arten von Orten gesucht, in dieser Reihenfolge:

1. im Benutzerordner (``daten_basis()/lunivo-office/<paket>``), dort legt der Benutzer Nachgeladenes ab,
2. beim Programm (``PROGRAMMORDNER/<paket>``), dort liegt Mitgeliefertes der Installationspakete,
3. in jedem Ordner der Umgebungsvariablen ``LUNIVO_ZUSATZPAKETE`` (mehrere durch das Pfadtrennzeichen des Systems getrennt), jeweils ``<ordner>/<paket>``.

Kein Ort ist an ein Betriebssystem oder einen Installationspfad gebunden.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from . import benutzerorte, ressourcen_pfade

UMGEBUNG = "LUNIVO_ZUSATZPAKETE"
ARGOS = "argos"
PIPER = "piper"
SCHRIFTEN = "schriften"
_ARGOS_ENDUNG = ".argosmodel"
_SCHRIFT_ENDUNGEN = (".ttf", ".otf", ".ttc")


@dataclass(frozen=True)
class Zusatzpaket:
    """Ein Zusatzpaket mit allen Suchorten und den Orten, an denen tatsächlich etwas gefunden wurde."""
    kennung: str
    suchorte: tuple[str, ...]
    fundorte: tuple[str, ...]

    @property
    def vorhanden(self) -> bool:
        return bool(self.fundorte)


def _zusatzwurzeln() -> list[str]:
    """Absolute Ordner aus ``LUNIVO_ZUSATZPAKETE``."""
    return [o for o in os.environ.get(UMGEBUNG, "").split(os.pathsep) if o and os.path.isabs(o)]


def _suchorte(paket: str) -> list[str]:
    benutzer = os.path.join(benutzerorte.daten_basis(), "lunivo-office", paket)
    programm = os.path.join(ressourcen_pfade.PROGRAMMORDNER, paket)
    return [benutzer, programm] + [os.path.join(o, paket) for o in _zusatzwurzeln()]


def argos_dirs() -> list[str]:
    """Suchorte für Argos-Sprachpakete (.argosmodel): Benutzerordner zuerst, dann der mitgelieferte Ordner beim Programm."""
    return _suchorte(ARGOS)


def argos_pakete_dir() -> str:
    """Beschreibbarer Ort, an dem Argos die installierten Sprachpakete ablegt (der mitgelieferte Ordner ist schreibgeschützt)."""
    pfad = os.path.join(benutzerorte.data_dir(), "argos-pakete")
    os.makedirs(pfad, exist_ok=True)
    return pfad


def piper_dirs() -> list[str]:
    """Suchorte für Piper und seine Stimmen (stimme-holen.sh), der erste ist der aktuelle."""
    orte = _suchorte(PIPER)
    aelter = os.path.join(benutzerorte.daten_basis(), "schreibhilfe", PIPER)
    return [orte[0], aelter] + orte[1:]


def _inhalt(ordner: str) -> list[str]:
    try:
        return os.listdir(ordner)
    except OSError:
        return []


def _mit_endung(ordner: str, endungen: tuple[str, ...]) -> bool:
    return any(name.lower().endswith(endungen) for name in _inhalt(ordner))


def zusatzpakete_erkennen() -> tuple[Zusatzpaket, ...]:
    """Alle Zusatzpakete mit ihren Suchorten und Fundorten; legt nichts an und lädt nichts."""
    argos = tuple(argos_dirs())
    piper = tuple(piper_dirs())
    schriften = (benutzerorte.schriften_dir(),) + tuple(_suchorte(SCHRIFTEN)[1:])
    return (
        Zusatzpaket(ARGOS, argos, tuple(o for o in argos if _mit_endung(o, (_ARGOS_ENDUNG,)))),
        Zusatzpaket(PIPER, piper, tuple(o for o in piper if _inhalt(o))),
        Zusatzpaket(SCHRIFTEN, schriften, tuple(o for o in schriften if _mit_endung(o, _SCHRIFT_ENDUNGEN))),
    )
