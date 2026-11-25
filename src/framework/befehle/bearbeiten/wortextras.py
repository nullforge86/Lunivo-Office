"""Wort-Extras (Start ▸ Wort-Extras): Absätze aufräumen – über die Markierung, sonst über das ganze Dokument.

Die Fachlogik liegt in ``core.text.wortextras``; hier läuft sie über den Änderungsrahmen. Das Menü gibt es als unveränderliche Daten."""
from __future__ import annotations

from core.text import AKTIONEN as _AKTIONEN, MENUE as _KERN_MENUE
from framework.befehle.aenderung import ausfuehren
from framework.schnittstellen.datentypen import Menueeintrag


def _eintrag(z) -> Menueeintrag:
    if z == "-":
        return Menueeintrag(trenner=True)
    text, symbol, ziel = z
    if isinstance(ziel, list):
        return Menueeintrag(text=text, symbol=symbol, unter=tuple(_eintrag(u) for u in ziel))
    return Menueeintrag(text=text, symbol=symbol, befehl=ziel)


MENUE: tuple[Menueeintrag, ...] = tuple(_eintrag(z) for z in _KERN_MENUE)


def wortextra_ausfuehren(kennung: int, befehl: str) -> int | None:
    """Führt den Wort-Extra-Befehl ``befehl`` für das Dokument aus. → Zahl der geänderten Stellen; ``None``, wenn nichts ausgeführt wurde."""
    arbeit = _AKTIONEN.get(befehl)
    if arbeit is None:
        raise KeyError(f"Unbekannter Wort-Extra-Befehl: {befehl}")
    return ausfuehren(kennung, arbeit)
