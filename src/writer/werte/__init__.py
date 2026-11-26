"""Tür des Pakets ``writer.werte``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Bereich": ("stellen", "Bereich"),
    "Bildfehler": ("fehler", "Bildfehler"),
    "Dateifehler": ("fehler", "Dateifehler"),
    "Groesse": ("geometrie", "Groesse"),
    "KennwortNoetig": ("fehler", "KennwortNoetig"),
    "Punkt": ("geometrie", "Punkt"),
    "Raender": ("geometrie", "Raender"),
    "Rechteck": ("geometrie", "Rechteck"),
    "Stelle": ("stellen", "Stelle"),
    "Vektorpfad": ("geometrie", "Vektorpfad"),
    "eigene_kopie": ("werte", "eigene_kopie"),
    "grundfarben": ("farben", "grundfarben"),
    "mm_zu_px": ("einheiten", "mm_zu_px"),
    "px_je_mm": ("einheiten", "px_je_mm"),
    "px_zu_mm": ("einheiten", "px_zu_mm"),
    "unveraenderlich": ("werte", "unveraenderlich"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "einheiten":
        from . import einheiten as _datei
    elif datei == "farben":
        from . import farben as _datei
    elif datei == "fehler":
        from . import fehler as _datei
    elif datei == "geometrie":
        from . import geometrie as _datei
    elif datei == "stellen":
        from . import stellen as _datei
    elif datei == "werte":
        from . import werte as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
