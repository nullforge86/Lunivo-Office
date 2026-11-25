"""Befehl und Ergebnis: der Hinweg von der Oberfläche zum Framework. Beides sind unveränderliche, Qt-freie Datentypen."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Befehl:
    name: str                                   # z. B. "text.fett"
    parameter: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Ergebnis:
    ok: bool = True
    text: str = ""
    daten: dict = field(default_factory=dict)
