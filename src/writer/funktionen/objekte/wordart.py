"""WordArt und Texteffekte: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import wordart as befehle
from framework.schnittstellen.datentypen.effektdaten import EffektDaten, EffektVorgabe

PX: float = befehle.PX
MATERIAL: tuple[tuple[str, str], ...] = befehle.MATERIAL
BELEUCHTUNG: tuple[tuple[str, str], ...] = befehle.BELEUCHTUNG
WARP_FORMEN: tuple[tuple[str, str], ...] = befehle.WARP_FORMEN


def schatten_vorgaben() -> tuple[EffektVorgabe, ...]:
    return befehle.schatten_vorgaben()


def reflektion_vorgaben() -> tuple[EffektVorgabe, ...]:
    return befehle.reflektion_vorgaben()


def leuchten_vorgaben() -> tuple[EffektVorgabe, ...]:
    return befehle.leuchten_vorgaben()


def wordart_vorgaben() -> tuple[EffektVorgabe, ...]:
    return befehle.wordart_vorgaben()


def hat_effekt(fx: EffektDaten | None) -> bool:
    return befehle.hat_effekt(fx)


def als_text(fx: EffektDaten | None) -> str:
    return befehle.als_text(fx)


def aus_text(text: str | None) -> EffektDaten:
    return befehle.aus_text(text)
