"""Deckblätter: die Namen der Gestaltungen in der Reihenfolge der Galerie. Die Fachdaten liegen im Kern; die Oberfläche erhält unveränderliche Werte."""
from __future__ import annotations

from core.dokument.abschnitte import deckblatt_vorlagen as modell

NAMEN: tuple[str, ...] = tuple(modell.NAMEN)
