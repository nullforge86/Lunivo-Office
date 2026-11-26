"""Tür des Pakets ``core.korrektur.silbentrennung``: öffentliche Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "trenner_fuer": ("trennung", "trenner_fuer"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "trennung":
        from . import trennung as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
