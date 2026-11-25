"""Anbindung der Oberfläche an ``framework.befehle.ansicht.vorlagen``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.befehle.ansicht as _fw
from framework.schnittstellen import Einstellungen


def vorlagen_ordner(e: Einstellungen) -> str:
    return _fw.vorlagen_ordner(e)
