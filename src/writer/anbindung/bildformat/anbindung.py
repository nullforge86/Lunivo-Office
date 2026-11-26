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
    from framework.schnittstellen import Bildfehler as _Bildfehler
    from writer.werte import Bildfehler
    try:
        return eigene_kopie(_fw.entpacken(blob, grenze))
    except _Bildfehler as e:
        raise Bildfehler(str(e)) from None


def format_erkennen(blob: bytes) -> str | None:
    """Das Bildformat am Dateikopf (nicht an der Endung); None, wenn es keines der bekannten ist."""
    return eigene_kopie(_fw.format_erkennen(blob))


def svg_masse(daten: bytes) -> tuple[float, float] | None:
    """Breite und Höhe eines SVG-Bildes."""
    return _fw.svg_masse(daten)
