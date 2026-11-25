"""Anbindung der Oberfläche an ``framework.befehle.datei.orte``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.befehle.datei as _fw


def data_dir() -> str:
    """Programmdaten des Benutzers; wird bei Bedarf angelegt."""
    return _fw.data_dir()
