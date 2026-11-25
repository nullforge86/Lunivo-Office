"""Unveränderliche Kopien reiner Daten des Kerns: Was das Framework an die Oberfläche weitergibt, ist nie ein Objekt des Kerns.

Listen werden zu ``FesteListe``, Mengen zu ``FesteMenge`` (beide unveränderlich), Wörterbücher zu schreibgeschützten Sichten.
So kann ``writer`` daraus für die Oberfläche eine eigene Kopie derselben Gestalt machen."""
from __future__ import annotations

from collections.abc import Collection, Hashable
from types import MappingProxyType

Daten = Collection | Hashable | None


class FesteListe(tuple):
    """Unveränderliche Kopie einer Liste des Kerns."""
    __slots__ = ()


class FesteMenge(frozenset):
    """Unveränderliche Kopie einer Menge des Kerns."""
    __slots__ = ()


def fest(wert: Daten) -> Daten:
    """Tiefe, unveränderliche Kopie: Wörterbuch → schreibgeschützte Sicht, Liste → ``FesteListe``, Menge → ``FesteMenge``."""
    if isinstance(wert, dict):
        return MappingProxyType({k: fest(v) for k, v in wert.items()})
    if isinstance(wert, list):
        return FesteListe(fest(v) for v in wert)
    if type(wert) is tuple:
        return tuple(fest(v) for v in wert)
    if isinstance(wert, set):
        return FesteMenge(wert)
    return wert
