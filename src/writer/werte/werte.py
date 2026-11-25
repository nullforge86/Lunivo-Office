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


def eigene_kopie(wert):
    """Eigene, veränderbare Kopie der Oberfläche aus einem festen Wert des Frameworks (gleiche Gestalt wie im Kern)."""
    from framework.anbindung import FesteListe, FesteMenge
    if isinstance(wert, MappingProxyType):
        return {k: eigene_kopie(v) for k, v in wert.items()}
    if isinstance(wert, FesteListe):
        return [eigene_kopie(v) for v in wert]
    if isinstance(wert, FesteMenge):
        return set(wert)
    if type(wert) is tuple:
        return tuple(eigene_kopie(v) for v in wert)
    return wert
