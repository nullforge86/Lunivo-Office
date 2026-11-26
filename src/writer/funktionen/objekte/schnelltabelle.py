"""Schnelltabellen: die Steuerung der Oberfläche. Reicht den Befehl an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import schnelltabelle as befehle
from writer.werte import unveraenderlich


def schnelltabellen_namen() -> tuple[str, ...]:
    return unveraenderlich(befehle.SCHNELLTABELLEN)

def einfuegen(kennung: int, name: str) -> bool:
    return befehle.einfuegen(kennung, name)
