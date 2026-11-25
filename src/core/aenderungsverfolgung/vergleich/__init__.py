"""Tür des Pakets ``core.aenderungsverfolgung.vergleich``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AEHNLICH": ("vergleich", "AEHNLICH"),
    "STANDARD": ("markup_filter", "STANDARD"),
    "TOKEN": ("vergleich", "TOKEN"),
    "anwenden": ("vergleich", "anwenden"),
    "bearbeiter": ("fassungen", "bearbeiter"),
    "ist_gefiltert": ("markup_filter", "ist_gefiltert"),
    "ist_sichtbar": ("markup_filter", "ist_sichtbar"),
    "ops_bestimmen": ("vergleich", "ops_bestimmen"),
    "original": ("fassungen", "original"),
    "vergleichen": ("vergleich", "vergleichen"),
    "zeiten": ("fassungen", "zeiten"),
    "zusammenfuehren": ("vergleich", "zusammenfuehren"),
    "zusammenlegen": ("vergleich", "zusammenlegen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "fassungen":
        from . import fassungen as _datei
    elif datei == "markup_filter":
        from . import markup_filter as _datei
    elif datei == "vergleich":
        from . import vergleich as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
