"""Anbindung der Oberfläche an ``core.korrektur.woerterbuecher.vorhersage`` über ``framework.anbindung.vorhersage``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import framework.anbindung.vorhersage as _fw
from writer.werte import eigene_kopie


@cache
def empfaenger():
    return eigene_kopie(_fw.empfaenger())


def faengt_an_mit(anfang: str, hoechstens: int = 8, gelernt: Mapping | None = None, thema: frozenset = frozenset()) -> Sequence[str]:
    return eigene_kopie(_fw.faengt_an_mit(anfang, hoechstens, gelernt, thema))


def thema_woerter(name: str) -> frozenset:
    return eigene_kopie(_fw.thema_woerter(name))
