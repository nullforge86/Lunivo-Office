"""Tür des Pakets ``core.diagramme.daten``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ELEMENTE": ("diagramm_zusatz", "ELEMENTE"),
    "ELEMENT_NAMEN": ("diagramm_zusatz", "ELEMENT_NAMEN"),
    "LEGENDEN_LAGEN": ("diagramm_zusatz", "LEGENDEN_LAGEN"),
    "STANDARD_ELEMENTE": ("diagramm_zusatz", "STANDARD_ELEMENTE"),
    "elemente_wirksam": ("diagramm_zusatz", "elemente_wirksam"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "diagramm_zusatz":
        from . import diagramm_zusatz as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
