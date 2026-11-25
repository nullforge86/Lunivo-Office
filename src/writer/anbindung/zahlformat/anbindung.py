"""Anbindung der Oberfläche an ``core.text.zahlformat`` über ``framework.anbindung.zahlformat``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.zahlformat as _fw
from writer.werte import eigene_kopie


@cache
def typen():
    return eigene_kopie(_fw.typen())


def zahl_text(n: int, typ: str) -> str:
    """Die Zahl im gewählten Typ; liegt sie außerhalb der Grenzen, ``ValueError``."""
    return eigene_kopie(_fw.zahl_text(n, typ))
