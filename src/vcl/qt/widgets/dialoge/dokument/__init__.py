"""Dokument-, Druck- und Exportbausteine. Tür des Pakets: Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen (keine zusätzlichen Importzyklen)."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Dateifenster": ("speichern_fenster", "Dateifenster"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "speichern_fenster":
        from . import speichern_fenster as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
