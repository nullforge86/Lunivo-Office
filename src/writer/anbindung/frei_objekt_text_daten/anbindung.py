"""Anbindung der Oberfläche an ``core.objekte.textfelder.modell.frei_objekt_text_daten`` über ``framework.anbindung.frei_objekt_text_daten``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import framework.anbindung.frei_objekt_text_daten as _fw
from writer.werte import eigene_kopie


@cache
def arten():
    return eigene_kopie(_fw.arten())


@cache
def form_standard():
    return eigene_kopie(_fw.form_standard())


@cache
def standard_mass():
    return eigene_kopie(_fw.standard_mass())


@cache
def textfeld_fuell():
    return eigene_kopie(_fw.textfeld_fuell())


@cache
def textfeld_rand():
    return eigene_kopie(_fw.textfeld_rand())


@cache
def text_arten():
    return eigene_kopie(_fw.text_arten())


def laeufe_ab(laeufe: Sequence[Mapping], von: int, bis: int | None = None) -> Sequence[Mapping]:
    """Der Ausschnitt ``[von, bis)`` des Gesamttextes mit seinen Formaten."""
    return eigene_kopie(_fw.laeufe_ab(laeufe, von, bis))


def laeufe_zusammen(laeufe: Sequence[Mapping]) -> Sequence[Mapping]:
    """Benachbarte Läufe mit gleichem Format zu einem verbinden (leere fallen weg)."""
    return eigene_kopie(_fw.laeufe_zusammen(laeufe))


@cache
def ss():
    """Faktor, in dem Objekte gezeichnet werden (doppelte Auflösung: scharf auch bei Zoom)."""
    return eigene_kopie(_fw.ss())


def gedreht(richtung: str | None) -> bool:
    """Läuft der Text nicht waagerecht?"""
    return _fw.gedreht(richtung)
