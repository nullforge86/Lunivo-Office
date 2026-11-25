"""Tür des Pakets ``core.korrektur.woerterbuecher``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "EMPFAENGER": ("vorhersage", "EMPFAENGER"),
    "HAEUFIG": ("haeufig", "HAEUFIG"),
    "faengt_an_mit": ("vorhersage", "faengt_an_mit"),
    "thema_aufnehmen": ("vorhersage", "thema_aufnehmen"),
    "thema_woerter": ("vorhersage", "thema_woerter"),
    "themenwoerter": ("vorhersage", "themenwoerter"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "haeufig":
        from . import haeufig as _datei
    elif datei == "vorhersage":
        from . import vorhersage as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
