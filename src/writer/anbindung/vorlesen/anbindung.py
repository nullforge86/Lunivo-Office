"""Vorlesen für die Oberfläche: reicht an den Vorlesedienst des Frameworks weiter. Fehler des Dienstes kommen als ``Vorlesefehler`` an."""
from __future__ import annotations

import framework.dokumentverwaltung.dokumentpflege as _fw
from framework.befehle import bearbeiten as _befehle


class Vorlesefehler(Exception):
    """Das Vorlesen ist nicht möglich — der Text ist für Anwender gedacht."""


def einstellung_stimme() -> str:
    """Schlüssel der Einstellung „Stimme“."""
    return _fw.EINSTELLUNG_STIMME


def einstellung_tempo() -> str:
    """Schlüssel der Einstellung „Tempo“."""
    return _fw.EINSTELLUNG_TEMPO


def tempo_grenzen() -> tuple[int, int, int]:
    """(kleinstes, größtes Tempo, Schritt) in Prozent: 0 = normal."""
    return _fw.TEMPO_MIN, _fw.TEMPO_MAX, _fw.TEMPO_SCHRITT


def piper_programm():
    return _fw.piper_programm()


def piper_stimmen() -> list[dict]:
    return [dict(s) for s in _fw.piper_stimmen()]


def piper_da() -> bool:
    return _fw.piper_da()


def verfuegbar() -> bool:
    return _fw.verfuegbar()


def stimmen() -> list[dict]:
    return [dict(s) for s in _fw.stimmen()]


def beenden() -> None:
    _fw.beenden()


def vorlesetext(kennung: int, von: int = 0, bis: int | None = None) -> str:
    """Der Text des Dokuments ``kennung`` von ``von`` bis ``bis`` (Stellen im Rohtext) zum Vorlesen."""
    return _befehle.abfragen_vorlesetext(kennung, von, bis)


def lies_vor(text: str, stimme: str = "", tempo: int = 0) -> bool:
    try:
        return _fw.lies_vor(text, stimme, tempo)
    except _fw.VorlesenFehler as e:
        raise Vorlesefehler(str(e)) from e
