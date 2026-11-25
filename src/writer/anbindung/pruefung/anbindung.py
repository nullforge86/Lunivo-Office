"""Anbindung der Oberfläche an ``core.korrektur.rechtschreibung.pruefung`` über ``framework.anbindung.pruefung``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.pruefung as _fw
from writer.werte import eigene_kopie


@cache
def pruefer_namen():
    return eigene_kopie(_fw.pruefer_namen())
