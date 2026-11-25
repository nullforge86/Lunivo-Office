"""Auswahllisten der Sendungen für die Oberfläche: Umschlagformate und Etikettenbögen als Namen (die Maße bleiben im Kern)."""
from __future__ import annotations

from core.funktionen.sendungen.etiketten import ETIKETTEN
from core.funktionen.sendungen.umschlag import UMSCHLAEGE


def umschlag_formate() -> tuple[str, ...]:
    return tuple(UMSCHLAEGE)


def etiketten_boegen() -> tuple[str, ...]:
    return tuple(ETIKETTEN)
