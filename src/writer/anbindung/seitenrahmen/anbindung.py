"""Anbindung der Oberfläche an ``core.layout.drucklayout.ausgabe.seite.seitenrahmen`` über ``framework.anbindung.seitenrahmen``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping

import framework.anbindung.seitenrahmen as _fw
from writer.werte import eigene_kopie


def abstaende_pt(b: Mapping) -> tuple[float, float, float, float]:
    """(oben, unten, links, rechts) in pt."""
    return eigene_kopie(_fw.abstaende_pt(b))
