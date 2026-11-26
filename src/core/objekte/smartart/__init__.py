"""Tür des Pakets ``core.objekte.smartart``: öffentliche Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "baum": ("smartart_zeichnen_daten", "baum"),
    "beginnen": ("smartart_zeichnen_daten", "beginnen"),
    "format_von": ("smartart_zeichnen_daten", "format_von"),
    "grundschrift_setzen": ("smartart_zeichnen_daten", "grundschrift_setzen"),
    "gruppen": ("smartart_zeichnen_daten", "gruppen"),
    "schrift": ("smartart_zeichnen_daten", "schrift"),
    "schrift_uebernehmen": ("smartart_zeichnen_daten", "schrift_uebernehmen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "smartart_zeichnen_daten":
        from . import smartart_zeichnen_daten as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
