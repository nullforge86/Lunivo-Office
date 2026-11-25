"""Anbindung der Oberfläche an ``framework.befehle.ansicht.einstellungen``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.befehle.ansicht as _fw
from framework.schnittstellen import Einstellungen


def oberflaeche_zuruecksetzen(e: Einstellungen) -> None:
    """Register, Schnellzugriff, ausgetauschte Symbole und Oberflächenart auf die Vorgabe zurücksetzen."""
    return _fw.oberflaeche_zuruecksetzen(e)


def symbolleisten_statt_register(e: Einstellungen) -> bool:
    return _fw.symbolleisten_statt_register(e)


def thema(e: Einstellungen) -> str:
    return _fw.thema(e)


def weich(e: Einstellungen) -> bool:
    return _fw.weich(e)
