"""Vektorbilder (EMF/WMF): reicht Erkennen, Größe und Rastern an das Framework weiter; die Oberfläche zeigt nur das fertige Bild."""
from __future__ import annotations

from framework.dokumentverwaltung.ausgabe import ist_emf, ist_wmf, masse_px
from framework.dokumentverwaltung.ausgabe import metafile_rgba as _rgba


def ist_metafile_emf(blob: bytes) -> bool:
    return ist_emf(blob)


def ist_metafile_wmf(blob: bytes) -> bool:
    return ist_wmf(blob)


def metafile_masse_px(blob: bytes) -> tuple[float, float] | None:
    return masse_px(blob)


def metafile_rgba(blob: bytes, breite_px: int = 0, hoehe_px: int = 0) -> tuple[int, int, bytes] | None:
    return _rgba(blob, breite_px, hoehe_px)
