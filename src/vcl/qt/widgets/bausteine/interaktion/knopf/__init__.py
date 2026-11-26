"""Der Knopf als Baustein aus Form, Inhalt und Verhalten (je eine Datei); ``knopf.py`` setzt sie zusammen.

Tür des Pakets: Aufrufer außerhalb importieren ``werkzeugknopf`` von hier. Die Datei wird erst beim ersten Zugriff geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "werkzeugknopf": ("knopf", "werkzeugknopf"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "knopf":
        from . import knopf as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
