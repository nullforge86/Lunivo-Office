"""Anbindung an ``core.objekte.bilder.modell.bildformat``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.objekte.bilder.modell as _k
from framework.anbindung import fest


@cache
def formate() -> Mapping[str, tuple[str, str]]:
    return fest(_k.FORMATE)


@cache
def max_entpackt_bytes() -> int:
    return fest(_k.MAX_ENTPACKT_BYTES)


def entpacken(blob: bytes, grenze: int = 52428800) -> bytes:
    """gzip-gepackte Bilddaten (SVGZ, EMZ, WMZ) entpacken, höchstens ``grenze`` Bytes; andere Daten bleiben unverändert."""
    from framework.schnittstellen import Bildfehler
    try:
        return fest(_k.entpacken(blob, grenze))
    except _k.BildFehler as e:
        raise Bildfehler(str(e)) from None


def format_erkennen(blob: bytes) -> str | None:
    """Das Bildformat am Dateikopf (nicht an der Endung); None, wenn es keines der bekannten ist."""
    return fest(_k.format_erkennen(blob))


def svg_masse(daten: bytes) -> tuple[float, float] | None:
    """Breite und Höhe eines SVG-Bildes (liest der Kern aus den Daten)."""
    from core.layout.drucklayout.ausgabe.bild import svg_masse as masse
    return masse(daten)
