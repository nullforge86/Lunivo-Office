"""Anbindung der Oberfläche an ``framework.befehle.ueberpruefen.einstellungen``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.befehle.ueberpruefen as _fw
from framework.schnittstellen import Einstellungen
from writer.werte import unveraenderlich


def ballon_werte():
    return unveraenderlich(_fw.BALLON_WERTE)


def ballons(e: Einstellungen) -> str:
    return _fw.ballons(e)


def ballons_setzen(e: Einstellungen, wert: str) -> None:
    return _fw.ballons_setzen(e, wert)
