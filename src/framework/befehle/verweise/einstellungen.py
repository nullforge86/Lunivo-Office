"""Einstellungen der Funktion „Verweise“: eigene Beschriftungsbezeichnungen."""
from __future__ import annotations

import json

from framework.schnittstellen.einstellungen import Einstellungen

BESCHRIFTUNGEN = "verweise/beschriftungen"


def eigene_beschriftungen(e: Einstellungen) -> tuple[str, ...]:
    try:
        return tuple(str(x) for x in json.loads(e.get(BESCHRIFTUNGEN, "[]") or "[]"))
    except (ValueError, TypeError):
        return ()


def eigene_beschriftungen_setzen(e: Einstellungen, eigene: list[str]) -> None:
    e.set(BESCHRIFTUNGEN, json.dumps(list(eigene), ensure_ascii=False))
