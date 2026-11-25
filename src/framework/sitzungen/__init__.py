"""Tür des Pakets ``framework.sitzungen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``. Nicht in der Tür: altlast."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "DocumentManager": ("dokumentverwaltung", "DocumentManager"),
    "Sitzung": ("dokumentsteuerung", "Sitzung"),
    "sitzung": ("dokumentsteuerung", "sitzung"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "dokumentsteuerung":
        from . import dokumentsteuerung as _datei
    elif datei == "dokumentverwaltung":
        from . import dokumentverwaltung as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
