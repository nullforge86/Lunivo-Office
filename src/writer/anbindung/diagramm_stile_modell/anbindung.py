"""Anbindung der Oberfläche an ``core.diagramme.formatierung.diagramm_stile_modell`` über ``framework.anbindung.diagramm_stile_modell``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import framework.anbindung.diagramm_stile_modell as _fw
from writer.werte import eigene_kopie


@cache
def stile():
    return eigene_kopie(_fw.stile())


@cache
def stil_extra():
    return eigene_kopie(_fw.stil_extra())


def stile_liste() -> Sequence[Mapping]:
    """Alle Formatvorlagen (Diagrammstile) für die Galerie: {nr, name, grund, schrift, raster, **Zusätze}."""
    return eigene_kopie(_fw.stile_liste())
