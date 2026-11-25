"""Anbindung an ``core.verzeichnisse.inhaltsverzeichnis.verzeichnis``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping
from functools import cache

import core.verzeichnisse.inhaltsverzeichnis as _k
from framework.anbindung import fest


@cache
def toc_vorgabe() -> Mapping[str, bool | int | str]:
    return fest(_k.TOC_VORGABE)
