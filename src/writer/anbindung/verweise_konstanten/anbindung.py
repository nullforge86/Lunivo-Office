"""Anbindung der Oberfläche an ``framework.befehle.verweise.konstanten``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.befehle.verweise as _fw
from writer.werte import unveraenderlich


def beschriftungs_bezeichnungen():
    return unveraenderlich(_fw.BESCHRIFTUNGS_BEZEICHNUNGEN)


def fuellzeichen():
    return unveraenderlich(_fw.FUELLZEICHEN)


def inhaltsverzeichnis_fuell():
    return unveraenderlich(_fw.INHALTSVERZEICHNIS_FUELL)


def inhaltsverzeichnis_vorgabe():
    return unveraenderlich(_fw.INHALTSVERZEICHNIS_VORGABE)


def nummerierungsformate():
    return unveraenderlich(_fw.NUMMERIERUNGSFORMATE)


def quellentypen():
    return unveraenderlich(_fw.QUELLENTYPEN)


def verweistypen():
    return unveraenderlich(_fw.VERWEISTYPEN)


def zitierweisen_namen():
    return unveraenderlich(_fw.ZITIERWEISEN_NAMEN)


def verweisen_auf(art: str) -> list[tuple[str, str]]:
    """Die Möglichkeiten „Verweisen auf“ zu einem Verweistyp als (Schlüssel, Text)."""
    return _fw.verweisen_auf(art)
