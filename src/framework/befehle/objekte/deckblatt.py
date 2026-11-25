"""Deckblätter: die Namen der Gestaltungen in der Reihenfolge der Galerie. Die Fachdaten liegen im Kern; die Oberfläche erhält unveränderliche Werte."""
from __future__ import annotations

from core.dokument.abschnitte import deckblatt_vorlagen as modell
from framework.befehle import ausfuehren

NAMEN: tuple[str, ...] = tuple(modell.NAMEN)


def entfernen(kennung: int) -> bool:
    """Nimmt das Deckblatt des Dokuments heraus (ein Rückgängig-Schritt). → ``False``, wenn es keines gab oder das Dokument schreibgeschützt ist."""
    return bool(ausfuehren(kennung, modell.entfernen))
