"""Tür des Pakets ``framework.befehle``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AUSWAHL": ("aenderung", "AUSWAHL"),
    "Ausfuehrung": ("befehlssteuerung", "Ausfuehrung"),
    "GEAENDERT": ("aenderung", "GEAENDERT"),
    "Verteiler": ("befehlssteuerung", "Verteiler"),
    "ausfuehren": ("aenderung", "ausfuehren"),
    "bewegen": ("aenderung", "bewegen"),
    "lesen": ("aenderung", "lesen"),
    "verteiler": ("befehlssteuerung", "verteiler"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "aenderung":
        from . import aenderung as _datei
    elif datei == "befehlssteuerung":
        from . import befehlssteuerung as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
