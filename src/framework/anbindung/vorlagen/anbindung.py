"""Anbindung an ``core.dokument.vorlagen``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import core.dokument as _k
from framework.anbindung import fest


def muster() -> Sequence[Mapping]:
    return fest(_k.vorlagen_muster())


def rubriken(ordner: str) -> tuple[Mapping[str, Sequence[str]], Sequence[str]]:
    """Der Vorlagenordner nach Rubriken: jeder Unterordner ist eine Rubrik (Name → Dateien); lose Dateien liegen im Ordner selbst."""
    return fest(_k.vorlagen_rubriken(ordner))
