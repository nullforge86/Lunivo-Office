"""Die benannten Grundfarben des Programms für die Oberfläche (``Farbe.AKZENT`` statt ``"#2f6fb5"``): der Farmwork reicht die Werte des Kerns durch.

Es sind nur Zeichenketten mit Farbwerten; die Oberfläche bezieht sie von hier und nie direkt aus dem Kern."""
from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType

from core.formatierung.farben.farben import Farbe

__all__ = ["Farbe", "grundfarben"]


Farbwert = str | None | tuple | Mapping[str, str]


def _fest(w: str | None | tuple | list | dict) -> Farbwert:
    """Unveränderliche Kopie eines Farbwerts: Folgen als Tupel, Tafeln als schreibgeschützte Wörterbücher."""
    if isinstance(w, dict):
        return MappingProxyType({k: _fest(v) for k, v in w.items()})
    if isinstance(w, (list, tuple)):
        return tuple(_fest(v) for v in w)
    return w


def grundfarben() -> Mapping[str, Farbwert]:
    """Name → Wert aller Grundfarben des Kerns – Werte, kein Objekt des Kerns: Farbtexte, ``None``, Folgen als Tupel und Tafeln als
    schreibgeschützte Wörterbücher."""
    return MappingProxyType({n: _fest(getattr(Farbe, n)) for n in dir(Farbe) if n.isupper()})
