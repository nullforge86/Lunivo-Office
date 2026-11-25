"""Tür des Pakets ``core.formatierung.absatz``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "FUELL": ("tabfuell", "FUELL"),
    "TAB_ARTEN": ("tabtext", "TAB_ARTEN"),
    "VORGABE": ("absatzoptionen", "VORGABE"),
    "als_text": ("absatzoptionen", "als_text"),
    "aus_docx": ("tabfuell", "aus_docx"),
    "aus_ppr": ("absatzoptionen", "aus_ppr"),
    "aus_text": ("absatzoptionen", "aus_text"),
    "in_ppr": ("absatzoptionen", "in_ppr"),
    "tabs_als_text": ("tabtext", "tabs_als_text"),
    "tabs_aus_text": ("tabtext", "tabs_aus_text"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "absatzoptionen":
        from . import absatzoptionen as _datei
    elif datei == "tabfuell":
        from . import tabfuell as _datei
    elif datei == "tabtext":
        from . import tabtext as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
