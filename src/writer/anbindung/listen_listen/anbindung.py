"""Anbindung der Oberfläche an ``core.listen.listen`` über ``framework.anbindung.listen_listen``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.listen_listen as _fw
from writer.werte import eigene_kopie


@cache
def platzhalter():
    return eigene_kopie(_fw.platzhalter())


@cache
def zeichen_der_aufzaehlung():
    return eigene_kopie(_fw.zeichen_der_aufzaehlung())
