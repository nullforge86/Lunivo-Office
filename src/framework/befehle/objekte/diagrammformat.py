"""Format der Diagrammteile und Textfelder: Auswahllisten (Strichtypen, Pfeile, vertikale Ausrichtung). Die Fachdaten liegen im Kern; die Oberfläche
erhält unveränderliche Werte."""
from __future__ import annotations

from core.diagramme.formatierung import diagramm_format_daten as modell

VERTIKAL: tuple[tuple[str, str], ...] = tuple((schluessel, name) for schluessel, name in modell.VERTIKAL)
STRICHTYPEN: tuple[tuple[str, str], ...] = tuple((schluessel, name) for schluessel, name in modell.STRICHTYPEN)
PFEILE: tuple[tuple[str, str], ...] = tuple((schluessel, name) for schluessel, name in modell.PFEILE)
PFEIL_GROESSEN: tuple[tuple[float, str], ...] = tuple((float(groesse), name) for groesse, name in modell.PFEIL_GROESSEN)


def strich_schluessel(art: str | None) -> str:
    """Der Schlüssel der Auswahl ``STRICHTYPEN`` zu einer gespeicherten Strichart (ältere Dokumente: ``gepunktet`` …)."""
    return modell.strich_schluessel(art)
