"""Listen an der Schreibmarke: ordnet die Bedienung den Framework-Befehlen zu."""
from __future__ import annotations

from framework.befehle import bearbeiten as _befehle
from writer.werte import eigene_kopie


def liste_spec(kennung: int) -> dict | None:
    """Beschreibung der Liste am Absatz der Schreibmarke (für die Listenfenster), ``None`` ohne Liste."""
    return eigene_kopie(_befehle.listen_liste_spec(kennung))


def liste_setzen(kennung: int, spec: dict) -> bool:
    """Wendet die Liste auf die Absätze der Auswahl an; ``False``, wenn der Kern ablehnt."""
    return _befehle.listen_liste_setzen(kennung, spec)
