"""Anbindung der Oberfläche an ``framework.befehle.ueberpruefen.anzeige``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.befehle.ueberpruefen as _fw
from writer.werte import unveraenderlich


def anzeigen():
    return unveraenderlich(_fw.ANZEIGEN)
