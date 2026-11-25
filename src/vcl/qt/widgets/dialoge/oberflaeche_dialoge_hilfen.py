"""Oberflaeche dialoge hilfen: aus ``vcl.qt.widgets.dialoge.oberflaeche_dialoge`` herausgelöst."""
from __future__ import annotations
import json
from PySide6.QtWidgets import QLabel
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil


def lade_json(settings, key: str, standard):
    try:
        v = json.loads(settings.get(key, "") or "null")
        return standard if v is None else v
    except ValueError:
        return standard


def _satz(text: str, gedaempft: bool = False) -> QLabel:
    """Erklärung über den Feldern: bricht um."""
    t = QLabel(text); t.setWordWrap(True)
    if gedaempft:
        hinweis_stil(t)
    return t
