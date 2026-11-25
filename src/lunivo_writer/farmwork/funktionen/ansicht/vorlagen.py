"""Vorlagenordner: der Ordner eigener Vorlagen (aus den Einstellungen oder der Vorgabe), bei Bedarf angelegt."""
from __future__ import annotations

import os

from lunivo_writer.editor.dokument import vorlagen
from lunivo_writer.farmwork.schnittstellen.einstellungen import Einstellungen


def vorlagen_ordner(e: Einstellungen) -> str:
    ordner = vorlagen.vorlagenordner(e)
    os.makedirs(ordner, exist_ok=True)
    return ordner
