"""Deckblätter: die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import deckblatt as befehle
from writer.werte import unveraenderlich


def deckblatt_namen() -> tuple[str, ...]:
    return unveraenderlich(befehle.NAMEN)

def deckblatt_entfernen(kennung: int) -> bool:
    return befehle.entfernen(kennung)


def deckblatt_felder(name: str, blatt_b: float, blatt_h: float, quer: bool, oben_px: float, links_px: float, rechts_px: float) -> list[tuple[str, dict, dict]]:
    """Die Textfelder der Gestaltung ``name`` für ein Blatt: je Feld (Text, Absatzformat, Zeichenformat) als eigene Kopien."""
    from writer.werte import eigene_kopie
    return [(text, eigene_kopie(af), eigene_kopie(zf)) for text, af, zf in befehle.felder_formate(name, blatt_b, blatt_h, quer, oben_px, links_px, rechts_px)]


def deckblatt_gruppe(name: str) -> str:
    """Die Gruppe der Galerie, zu der die Gestaltung ``name`` gehört."""
    return befehle.gruppe(name)
