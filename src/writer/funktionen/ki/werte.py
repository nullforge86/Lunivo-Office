"""Unveränderliche Werte für die Oberfläche: Was ``writer`` aus dem Framework weitergibt, geht als Kopie hinaus, nie als Objekt des Frameworks."""
from __future__ import annotations

from types import MappingProxyType


def unveraenderlich(wert):
    """Unveränderliche Kopie: Listen und Tupel als Tupel, Wörterbücher als schreibgeschützte Sicht, Mengen als ``frozenset``."""
    if isinstance(wert, dict):
        return MappingProxyType({k: unveraenderlich(v) for k, v in wert.items()})
    if isinstance(wert, (list, tuple)):
        return tuple(unveraenderlich(v) for v in wert)
    if isinstance(wert, set):
        return frozenset(wert)
    return wert
