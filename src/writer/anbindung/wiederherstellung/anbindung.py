"""Anbindung der Oberfläche an ``framework.dokumentverwaltung.dokumentpflege.wiederherstellung``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.dokumentverwaltung.dokumentpflege as _fw


def new_token() -> str:
    return _fw.new_token()


def recovery_dir() -> str:
    return _fw.recovery_dir()
