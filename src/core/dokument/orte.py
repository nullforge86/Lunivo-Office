"""Orte außerhalb des Kerns, die er braucht: Programmdaten, Vorlagenordner und Schriftordner.

Der Kern liest nie aus ``system``. Das Framework meldet die Orte beim Programmstart an (``framework.dokumentverwaltung.kernorte``); der Kern fragt sie hier ab."""
from __future__ import annotations

from collections.abc import Callable

_ressourcen: str | None = None
_vorlagen: Callable[[], str] | None = None
_schriften: Callable[[], tuple[str, ...]] | None = None


def anmelden(ressourcen: str, vorlagen: Callable[[], str], schriften: Callable[[], tuple[str, ...]]) -> None:
    """Das Framework meldet den Ordner der Programmdaten und je einen Anbieter für den Vorlagenordner und die Schriftordner an."""
    global _ressourcen, _vorlagen, _schriften
    _ressourcen, _vorlagen, _schriften = ressourcen, vorlagen, schriften


def _angemeldet() -> None:
    if _ressourcen is None or _vorlagen is None or _schriften is None:
        raise RuntimeError("Die Orte des Kerns sind nicht angemeldet: zuerst ``framework`` importieren (``framework.dokumentverwaltung.kernorte``).")


def ressourcen() -> str:
    """Ordner der Programmdaten (Wortschatz, Vorlagenmuster, Texte)."""
    _angemeldet()
    return _ressourcen


def vorlagen_dir() -> str:
    """Standardordner der eigenen Vorlagen."""
    _angemeldet()
    return _vorlagen()


def schrift_ordner() -> tuple[str, ...]:
    """Die Ordner, in denen Schriften liegen."""
    _angemeldet()
    return _schriften()
