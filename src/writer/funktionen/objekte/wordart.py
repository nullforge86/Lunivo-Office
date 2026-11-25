"""WordArt und Texteffekte: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import wordart as befehle
from framework.schnittstellen.datentypen.effektdaten import EffektDaten, EffektVorgabe
from writer.werte import unveraenderlich


def wordart_px() -> float:
    return float(befehle.PX)


def wordart_materialien() -> tuple[tuple[str, str], ...]:
    return unveraenderlich(befehle.MATERIAL)


def wordart_beleuchtungen() -> tuple[tuple[str, str], ...]:
    return unveraenderlich(befehle.BELEUCHTUNG)


def wordart_warp_formen() -> tuple[tuple[str, str], ...]:
    return unveraenderlich(befehle.WARP_FORMEN)

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
