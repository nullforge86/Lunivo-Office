"""Anbindung an ``core.layout.drucklayout.ausgabe.text.wordartobjekt``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from functools import cache

import core.layout.drucklayout.ausgabe.text as _k
from framework.anbindung import fest


@cache
def zeichen_schluessel() -> tuple[str, ...]:
    return fest(_k.ZEICHEN_SCHLUESSEL)


def anzeige_laeufe(d: Mapping) -> Sequence[Mapping]:
    """Die Läufe, die das Objekt zeigt: ``[{"t": Text, <Zeichenschlüssel>…}]`` (Schlüssel, die fehlen, gelten für das ganze Objekt)."""
    return fest(_k.anzeige_laeufe(d))


def laeufe_text(laeufe: Sequence[Mapping]) -> str:
    return fest(_k.laeufe_text(laeufe))


def zeilen_laeufe(laeufe: Sequence[Mapping]) -> Sequence[Sequence[Mapping]]:
    """Läufe in Zeilen (Absätze) teilen."""
    return fest(_k.zeilen_laeufe(laeufe))
