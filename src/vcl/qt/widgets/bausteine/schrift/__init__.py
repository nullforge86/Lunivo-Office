"""Schriften und Texte der Oberfläche.

Tür des Pakets: Aufrufer außerhalb importieren die hier genannten Namen von hier. Die Datei wird erst beim ersten Zugriff geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "hinweis_label": ("texte", "hinweis_label"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "texte":
        from . import texte as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
