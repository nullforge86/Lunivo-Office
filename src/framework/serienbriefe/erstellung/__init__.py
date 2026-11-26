"""Tür des Pakets ``framework.serienbriefe.erstellung``: öffentliche Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "brief_fuer": ("serienbrief", "brief_fuer"),
    "gruppen": ("serienbrief", "gruppen"),
    "serienbrief_erzeugen": ("serienbrief", "serienbrief_erzeugen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "serienbrief":
        from . import serienbrief as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
