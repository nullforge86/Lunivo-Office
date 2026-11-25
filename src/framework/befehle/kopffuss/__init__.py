"""Tür des Pakets ``framework.befehle.kopffuss``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ALLE_FELDER": ("menues", "ALLE_FELDER"),
    "AUSRICHTUNGEN": ("menues", "AUSRICHTUNGEN"),
    "KEINE_NAECHSTE": ("befehle", "KEINE_NAECHSTE"),
    "KEINE_VORIGE": ("befehle", "KEINE_VORIGE"),
    "KEIN_VORGAENGER": ("befehle", "KEIN_VORGAENGER"),
    "KopfFussBefehle": ("befehle", "KopfFussBefehle"),
    "KopfFussOptionen": ("typen", "KopfFussOptionen"),
    "MenueEintrag": ("typen", "MenueEintrag"),
    "TRENNER": ("typen", "TRENNER"),
    "einstellungen": ("menues", "einstellungen"),
    "gruppe": ("menues", "gruppe"),
    "linie": ("menues", "linie"),
    "zone": ("menues", "zone"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "befehle":
        from . import befehle as _datei
    elif datei == "menues":
        from . import menues as _datei
    elif datei == "typen":
        from . import typen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
