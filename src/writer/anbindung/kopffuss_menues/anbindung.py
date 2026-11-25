"""Anbindung der Oberfläche an ``framework.befehle.kopffuss.menues``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.befehle.kopffuss as _fw
from framework.befehle.kopffuss import MenueEintrag as MenueEintrag


def einstellungen() -> tuple[MenueEintrag, ...]:
    return _fw.einstellungen()


def gruppe(bearbeitung_aktiv: bool) -> tuple[MenueEintrag, ...]:
    return _fw.gruppe(bearbeitung_aktiv)


def linie() -> tuple[MenueEintrag, ...]:
    return _fw.linie()


def zone(zone_name: str) -> tuple[MenueEintrag, ...]:
    return _fw.zone(zone_name)
