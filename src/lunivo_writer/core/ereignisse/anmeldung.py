"""Ereignis-Anmeldung im Kern: Der Kern meldet Ereignisse an Empfänger, die nur das Framework bei ihm anmeldet.

Angenommen werden ausschließlich Empfänger, deren Modul mit ``lunivo_writer.farmwork`` beginnt; alles andere wird abgewiesen. Der Kern
importiert das Framework nicht und ruft nie Rückrufe der Oberfläche auf."""
from __future__ import annotations

from collections.abc import Callable

_ERLAUBTES_MODUL = "lunivo_writer.farmwork"
_empfaenger: list[Callable[..., None]] = []


def anmelden(empfaenger: Callable[..., None]) -> None:
    modul = getattr(empfaenger, "__module__", "") or ""
    if not (modul == _ERLAUBTES_MODUL or modul.startswith(_ERLAUBTES_MODUL + ".")):
        raise PermissionError(f"Der Kern nimmt nur Empfänger aus {_ERLAUBTES_MODUL} an, nicht aus {modul or '?'}")
    if empfaenger not in _empfaenger:
        _empfaenger.append(empfaenger)


def melden(art: str, daten: dict | None = None) -> None:
    for empfaenger in list(_empfaenger):
        empfaenger(art, daten or {})
