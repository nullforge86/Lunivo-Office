"""Anbindung der Oberfläche an ``core.formatierung.schrift.zeichenzusatz`` über ``framework.anbindung.zeichenzusatz``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.zeichenzusatz as _fw
from writer.werte import eigene_kopie


@cache
def ausrichtungen():
    return eigene_kopie(_fw.ausrichtungen())


@cache
def formen():
    return eigene_kopie(_fw.formen())


@cache
def vorlagen():
    return eigene_kopie(_fw.vorlagen())


def ruby_text(ruby: str, ausrichtung: str = 'zentriert', abstand: float = 0.0, groesse: float = 7.0) -> str:
    return eigene_kopie(_fw.ruby_text(ruby, ausrichtung, abstand, groesse))


def umschlossen_text(form: str, vorlage: str) -> str:
    return eigene_kopie(_fw.umschlossen_text(form, vorlage))
