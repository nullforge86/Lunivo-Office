"""Tür des Pakets ``core.verzeichnisse.inhaltsverzeichnis``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ARTEN": ("verzeichnis", "ARTEN"),
    "TOC_FUELL": ("verzeichnis", "TOC_FUELL"),
    "TOC_VORGABE": ("verzeichnis", "TOC_VORGABE"),
    "index_zeilen_bilden": ("verzeichnis_kern", "index_zeilen_bilden"),
    "toc_opt_lesen": ("verzeichnis", "toc_opt_lesen"),
    "toc_opt_text": ("verzeichnis", "toc_opt_text"),
    "toc_optionen": ("verzeichnis", "toc_optionen"),
    "verzeichnis_aktualisieren": ("verzeichnis", "verzeichnis_aktualisieren"),
    "verzeichnis_einfuegen": ("verzeichnis", "verzeichnis_einfuegen"),
    "vorhanden": ("verzeichnis", "vorhanden"),
    "zeilen_fuer": ("verzeichnis", "zeilen_fuer"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "verzeichnis":
        from . import verzeichnis as _datei
    elif datei == "verzeichnis_kern":
        from . import verzeichnis_kern as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
