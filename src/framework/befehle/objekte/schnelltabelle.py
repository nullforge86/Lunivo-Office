"""Schnelltabellen (Einfügen ▸ Tabelle ▸ Schnelltabellen): Die Tabelle entsteht im Kern; geändert wird über den Anschluss des Editors (``AenderungsPort``)."""
from __future__ import annotations

from core.tabellen.modell import tabelle_einfuegen as modell
from framework.schnittstellen.aenderungs_port import AenderungsPort

SCHNELLTABELLEN: tuple[str, ...] = tuple(modell.SCHNELLTABELLEN)


def einfuegen(editor: AenderungsPort, name: str) -> None:
    """Fügt die Schnelltabelle ``name`` an der Schreibmarke ein."""
    modell.schnelltabelle(editor.aendern, name)
