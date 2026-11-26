"""Vorlagenordner: der Ordner eigener Vorlagen (aus den Einstellungen oder der Vorgabe), bei Bedarf angelegt."""
from __future__ import annotations

import os

from core.dokument import vorlagen
from framework.schnittstellen.einstellungen import Einstellungen


def vorlagen_ordner_pfad(e: Einstellungen) -> str:
    """Der Vorlagenordner laut Einstellungen (ohne ihn anzulegen)."""
    return vorlagen.vorlagenordner(e)


def vorlagen_ordner(e: Einstellungen) -> str:
    ordner = vorlagen.vorlagenordner(e)
    os.makedirs(ordner, exist_ok=True)
    return ordner
