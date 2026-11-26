"""Anbindung der Oberfläche an ``core.diagramme.formatierung.diagramm_format_daten`` über ``framework.anbindung.diagramm_format_daten``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import framework.anbindung.diagramm_format_daten as _fw
from writer.werte import eigene_kopie


@cache
def fx_nur_hinter():
    return eigene_kopie(_fw.fx_nur_hinter())


@cache
def fx_schluessel():
    return eigene_kopie(_fw.fx_schluessel())


@cache
def px_pt():
    return eigene_kopie(_fw.px_pt())


def effekt_von(t: Mapping | None) -> Mapping:
    return eigene_kopie(_fw.effekt_von(t))


def feld_von(t: Mapping | None, teil: str | None = None) -> Mapping:
    """Das Textfeld eines Teils mit Vorgaben; ``teil="titel"`` belegt die Ränder vor (``RAENDER_TITEL``), alle anderen Teile bleiben bei 0."""
    return eigene_kopie(_fw.feld_von(t, teil))


def fuell_dict(f):
    """Die Füllung als Wörterbuch (dasselbe Wörterbuch, wenn schon eines übergeben ist); None bei Automatisch und bei „Keine Füllung“."""
    return _fw.fuell_dict(f)


def linie_keine(linie) -> bool:
    return _fw.linie_keine(linie)
