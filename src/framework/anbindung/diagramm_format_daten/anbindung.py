"""Anbindung an ``core.diagramme.formatierung.diagramm_format_daten``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.diagramme.formatierung as _k
from framework.anbindung import fest


@cache
def fx_nur_hinter() -> tuple[str, str, str, str]:
    return fest(_k.FX_NUR_HINTER)


@cache
def fx_schluessel() -> tuple[str, ...]:
    return fest(_k.FX_SCHLUESSEL)


@cache
def px_pt() -> float:
    return fest(_k.PX_PT)


def effekt_von(t: Mapping | None) -> Mapping:
    return fest(_k.effekt_von(t))


def feld_von(t: Mapping | None, teil: str | None = None) -> Mapping:
    """Das Textfeld eines Teils mit Vorgaben; ``teil="titel"`` belegt die Ränder vor (``RAENDER_TITEL``), alle anderen Teile bleiben bei 0."""
    return fest(_k.feld_von(t, teil))
