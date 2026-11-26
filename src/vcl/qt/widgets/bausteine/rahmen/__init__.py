"""Rahmen, Linien und Schatten der Oberfläche.

Tür des Pakets: Aufrufer außerhalb importieren die hier genannten Namen von hier. Die Datei wird erst beim ersten Zugriff geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "blattschatten": ("schatten", "blattschatten"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "schatten":
        from . import schatten as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
