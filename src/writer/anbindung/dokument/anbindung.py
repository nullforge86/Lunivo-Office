"""Anbindung der Oberfläche an ``core.dokument.dokument`` über ``framework.anbindung.dokument``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.dokument as _fw
from writer.werte import eigene_kopie


@cache
def aufzaehlungen():
    return eigene_kopie(_fw.aufzaehlungen())


@cache
def listen_ebenen():
    return eigene_kopie(_fw.listen_ebenen())
