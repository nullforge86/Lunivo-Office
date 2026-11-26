"""Schnelltabellen (Einfügen ▸ Tabelle ▸ Schnelltabellen): Die Tabelle entsteht im Kern, im Dokument der Kennung."""
from __future__ import annotations

from core.tabellen.modell import tabelle_einfuegen as modell
from framework.sitzungen import sitzung as _steuerung

SCHNELLTABELLEN: tuple[str, ...] = tuple(modell.SCHNELLTABELLEN)


def einfuegen(kennung: int, name: str) -> bool:
    """Fügt die Schnelltabelle ``name`` an der Schreibmarke ein; ``False``, wenn der Kern ablehnt."""
    from core.bearbeitung import BearbeitungsFehler
    sitzung = _steuerung._sitzungen[kennung].sitzung
    try:
        modell.schnelltabelle(lambda aenderung: aenderung(sitzung), name)
    except BearbeitungsFehler:
        return False
    return True
