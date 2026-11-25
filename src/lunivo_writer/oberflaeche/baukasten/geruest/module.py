"""Modulregister — jedes Modul meldet sich selbst an; Rahmen (Dashboards, Fenster) fragen das Register, statt Listen zu führen.

``anmelden(bereich, schluessel, titel, bauer, rang)``: ``titel`` ist ein Stichwort aus ``texte.json``, ``bauer`` der Name der Methode (oder
eine Funktion), die den Inhalt des Moduls baut. ``liste(bereich)`` gibt die Module nach ``rang`` geordnet zurück. Ein neues Modul braucht
nur seine eigene Anmeldung — kein Rahmen muss geändert werden."""
from __future__ import annotations

from typing import NamedTuple


class Modul(NamedTuple):
    schluessel: str
    titel: str
    bauer: object
    rang: int


_REGISTER: dict[str, dict[str, Modul]] = {}


def anmelden(bereich: str, schluessel: str, titel: str, bauer, rang: int = 100) -> None:
    _REGISTER.setdefault(bereich, {})[schluessel] = Modul(schluessel, titel, bauer, rang)


def liste(bereich: str) -> list[Modul]:
    return sorted(_REGISTER.get(bereich, {}).values(), key=lambda m: (m.rang, m.schluessel))
