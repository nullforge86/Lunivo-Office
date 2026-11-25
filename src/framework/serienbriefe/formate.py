"""Auswahllisten der Sendungen für die Oberfläche: Umschlagformate und Etikettenbögen als Namen (die Maße bleiben im Kern)."""
from __future__ import annotations

from framework.serienbriefe.erstellung.etiketten import ETIKETTEN
from framework.serienbriefe.erstellung.umschlag import UMSCHLAEGE


def umschlag_formate() -> tuple[str, ...]:
    return tuple(UMSCHLAEGE)


def etiketten_boegen() -> tuple[str, ...]:
    return tuple(ETIKETTEN)
