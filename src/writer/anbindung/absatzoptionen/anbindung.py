"""Anbindung der Oberfläche an ``core.formatierung.absatz.absatzoptionen`` über ``framework.anbindung.absatzoptionen``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.absatzoptionen as _fw
from writer.werte import eigene_kopie


@cache
def vorgabe():
    return eigene_kopie(_fw.vorgabe())


def aus_text(text: str) -> dict:
    """Die Absatzoptionen aus ihrer Textform (eigene Kopie)."""
    return eigene_kopie(_fw.aus_text(text))


def als_text(optionen: dict) -> str:
    """Die Absatzoptionen als Text für das Absatzformat."""
    return _fw.als_text(optionen)
