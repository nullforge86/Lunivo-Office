"""Anbindung der Oberfläche an ``framework.befehle.datei.einstellungen``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.befehle.datei as _fw
from framework.schnittstellen import Einstellungen


def letztes_dokument_oeffnen(e: Einstellungen) -> bool:
    return _fw.letztes_dokument_oeffnen(e)
