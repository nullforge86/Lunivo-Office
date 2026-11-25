"""Sprache der Rechtschreib- und Grammatikprüfung (Einstellung): reicht an das Framework weiter."""
from __future__ import annotations

from framework.befehle.korrektur import pruefsprache as _lesen, pruefsprache_setzen as _setzen
from framework.schnittstellen import Einstellungen


def pruefsprache(e: Einstellungen) -> str:
    return _lesen(e)


def pruefsprache_setzen(e: Einstellungen, kennung: str) -> None:
    _setzen(e, kennung)
