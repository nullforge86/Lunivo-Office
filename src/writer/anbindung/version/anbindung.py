"""Anbindung der Oberfläche an ``framework.schnittstellen.version``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.schnittstellen as _fw


def version():
    return _fw.programmversion()
