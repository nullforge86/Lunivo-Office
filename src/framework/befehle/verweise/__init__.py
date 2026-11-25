"""Tür des Pakets ``framework.befehle.verweise``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "BESCHRIFTUNGEN": ("einstellungen", "BESCHRIFTUNGEN"),
    "BESCHRIFTUNGS_BEZEICHNUNGEN": ("konstanten", "BESCHRIFTUNGS_BEZEICHNUNGEN"),
    "BeschriftungsStart": ("typen", "BeschriftungsStart"),
    "FUELLZEICHEN": ("konstanten", "FUELLZEICHEN"),
    "INHALTSVERZEICHNIS_FUELL": ("konstanten", "INHALTSVERZEICHNIS_FUELL"),
    "INHALTSVERZEICHNIS_VORGABE": ("konstanten", "INHALTSVERZEICHNIS_VORGABE"),
    "IndexEintrag": ("typen", "IndexEintrag"),
    "IndexStart": ("typen", "IndexStart"),
    "NUMMERIERUNGSFORMATE": ("konstanten", "NUMMERIERUNGSFORMATE"),
    "QUELLENTYPEN": ("konstanten", "QUELLENTYPEN"),
    "VERWEISTYPEN": ("konstanten", "VERWEISTYPEN"),
    "VerweiseBefehle": ("befehle", "VerweiseBefehle"),
    "ZITIERWEISEN_NAMEN": ("konstanten", "ZITIERWEISEN_NAMEN"),
    "eigene_beschriftungen": ("einstellungen", "eigene_beschriftungen"),
    "eigene_beschriftungen_setzen": ("einstellungen", "eigene_beschriftungen_setzen"),
    "verweisen_auf": ("konstanten", "verweisen_auf"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "befehle":
        from . import befehle as _datei
    elif datei == "einstellungen":
        from . import einstellungen as _datei
    elif datei == "konstanten":
        from . import konstanten as _datei
    elif datei == "typen":
        from . import typen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
