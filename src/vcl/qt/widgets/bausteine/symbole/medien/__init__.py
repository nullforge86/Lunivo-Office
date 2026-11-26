"""Medien- und Bildbausteine. Tür des Pakets: Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen (keine zusätzlichen Importzyklen)."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "BILD_FILTER": ("bildformate", "BILD_FILTER"),
    "seitenzahl_zeichner": ("seiten_bildchen", "seitenzahl_zeichner"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "bildformate":
        from . import bildformate as _datei
    elif datei == "seiten_bildchen":
        from . import seiten_bildchen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
