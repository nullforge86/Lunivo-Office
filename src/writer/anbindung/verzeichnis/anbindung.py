"""Anbindung der Oberfläche an ``core.verzeichnisse.inhaltsverzeichnis.verzeichnis`` über ``framework.anbindung.verzeichnis``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.verzeichnis as _fw
from writer.werte import eigene_kopie


@cache
def toc_vorgabe():
    return eigene_kopie(_fw.toc_vorgabe())
