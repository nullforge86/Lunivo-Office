"""Anbindung an ``core.diagramme.formatierung.diagramm_stile_modell``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import core.diagramme.formatierung as _k
from framework.anbindung import fest


@cache
def stile() -> Sequence[tuple[str, str, str, bool]]:
    return fest(_k.STILE)


@cache
def stil_extra() -> Mapping[int, Mapping[str, bool | int | str] | Mapping[str, bool | int] | Mapping[str, bool] | Mapping[str, str]]:
    return fest(_k.STIL_EXTRA)


def stile_liste() -> Sequence[Mapping]:
    """Alle Formatvorlagen (Diagrammstile) für die Galerie: {nr, name, grund, schrift, raster, **Zusätze}."""
    return fest(_k.stile_liste())
