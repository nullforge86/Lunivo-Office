"""Umwandlung zwischen den unveränderlichen Effektbeschreibungen des Frameworks und den Wörterbüchern, mit denen die Darstellung der Effekte arbeitet."""
from __future__ import annotations

from writer.funktionen.objekte.wordart import EffektDaten


def _wert_zu_dict(w):
    if isinstance(w, EffektDaten):
        return zu_dict(w)
    if isinstance(w, tuple):
        return [_wert_zu_dict(x) for x in w]
    return w


def zu_dict(e: EffektDaten | None) -> dict:
    """Eine neue, veränderbare Kopie des Effekts."""
    return {k: _wert_zu_dict(v) for k, v in e.werte} if e is not None else {}


def _wert_zu_daten(w):
    if isinstance(w, dict):
        return zu_daten(w)
    if isinstance(w, (list, tuple)):
        return tuple(_wert_zu_daten(x) for x in w)
    return w


def zu_daten(d: dict | None) -> EffektDaten | None:
    """Die unveränderliche Beschreibung zu einem Effekt-Wörterbuch (``None`` bleibt ``None``)."""
    return None if d is None else EffektDaten(tuple((k, _wert_zu_daten(v)) for k, v in d.items()))
