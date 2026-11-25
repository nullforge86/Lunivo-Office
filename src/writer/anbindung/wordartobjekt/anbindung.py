"""Anbindung der Oberfläche an ``core.layout.drucklayout.ausgabe.text.wordartobjekt`` über ``framework.anbindung.wordartobjekt``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import framework.anbindung.wordartobjekt as _fw
from writer.werte import eigene_kopie


@cache
def zeichen_schluessel():
    return eigene_kopie(_fw.zeichen_schluessel())


def anzeige_laeufe(d: Mapping) -> Sequence[Mapping]:
    """Die Läufe, die das Objekt zeigt: ``[{"t": Text, <Zeichenschlüssel>…}]`` (Schlüssel, die fehlen, gelten für das ganze Objekt)."""
    return eigene_kopie(_fw.anzeige_laeufe(d))


def laeufe_text(laeufe: Sequence[Mapping]) -> str:
    return eigene_kopie(_fw.laeufe_text(laeufe))


def zeilen_laeufe(laeufe: Sequence[Mapping]) -> Sequence[Sequence[Mapping]]:
    """Läufe in Zeilen (Absätze) teilen."""
    return eigene_kopie(_fw.zeilen_laeufe(laeufe))
