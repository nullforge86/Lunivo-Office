"""Anbindung der Oberfläche an ``core.dokument.felder_text_kern`` über ``framework.anbindung.felder_text_kern``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations


import framework.anbindung.felder_text_kern as _fw
from writer.werte import eigene_kopie


def ohne_schalter(anweisung: str) -> str:
    return eigene_kopie(_fw.ohne_schalter(anweisung))
