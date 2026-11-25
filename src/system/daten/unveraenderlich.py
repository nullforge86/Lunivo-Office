"""Unveränderliche Daten: Wörterbücher und Listen (wie sie das Dokumentformat kennt) einfrieren und als eigene, veränderbare Kopie wieder auftauen."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import MappingProxyType

Daten = Mapping[str, "Daten | str | int | float | bool | None | tuple"]


def einfrieren(wert):
    """Eine tiefe, unveränderliche Kopie: Wörterbücher werden schreibgeschützte Abbilder, Listen werden Tupel."""
    if isinstance(wert, Mapping):
        return MappingProxyType({k: einfrieren(v) for k, v in wert.items()})
    if isinstance(wert, (list, tuple)):
        return tuple(einfrieren(v) for v in wert)
    return wert


def auftauen(wert):
    """Eine tiefe, veränderbare Kopie: schreibgeschützte Abbilder werden Wörterbücher, Tupel werden Listen."""
    if isinstance(wert, Mapping):
        return {k: auftauen(v) for k, v in wert.items()}
    if isinstance(wert, Sequence) and not isinstance(wert, (str, bytes)):
        return [auftauen(v) for v in wert]
    return wert
