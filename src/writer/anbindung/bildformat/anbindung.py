"""Anbindung der Oberfläche an ``core.objekte.bilder.modell.bildformat`` über ``framework.anbindung.bildformat``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from functools import cache

import framework.anbindung.bildformat as _fw
from writer.werte import eigene_kopie


@cache
def formate():
    return eigene_kopie(_fw.formate())


@cache
def max_entpackt_bytes():
    return eigene_kopie(_fw.max_entpackt_bytes())


def entpacken(blob: bytes, grenze: int = 52428800) -> bytes:
    """gzip-gepackte Bilddaten (SVGZ, EMZ, WMZ) entpacken, höchstens ``grenze`` Bytes; andere Daten bleiben unverändert."""
    return eigene_kopie(_fw.entpacken(blob, grenze))


def format_erkennen(blob: bytes) -> str | None:
    """Das Bildformat am Dateikopf (nicht an der Endung); None, wenn es keines der bekannten ist."""
    return eigene_kopie(_fw.format_erkennen(blob))
