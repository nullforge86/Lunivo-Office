"""Tür des Pakets ``framework.schnittstellen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Bildfehler": ("fehler", "Bildfehler"),
    "BlasenEinstellung": ("sprechblasen", "BlasenEinstellung"),
    "BlasenKatalog": ("sprechblasen", "BlasenKatalog"),
    "BlasenSchrift": ("sprechblasen", "BlasenSchrift"),
    "Dateifehler": ("fehler", "Dateifehler"),
    "ERSTSTART_MARKE": ("einstellungen", "ERSTSTART_MARKE"),
    "EditorPort": ("dokument", "EditorPort"),
    "Einstellungen": ("einstellungen", "Einstellungen"),
    "KennwortNoetig": ("fehler", "KennwortNoetig"),
    "MAX_ZULETZT": ("einstellungen", "MAX_ZULETZT"),
    "ORGANISATION": ("einstellungen", "ORGANISATION"),
    "PROGRAMM": ("einstellungen", "PROGRAMM"),
    "SeitenPort": ("seiten_port", "SeitenPort"),
    "SilbenEinstellung": ("silbenfarben", "SilbenEinstellung"),
    "SilbenKatalog": ("silbenfarben", "SilbenKatalog"),
    "SmartArtKatalog": ("smartart", "SmartArtKatalog"),
    "SmartArtLayout": ("smartart", "SmartArtLayout"),
    "Sprechblase": ("sprechblasen", "Sprechblase"),
    "VorschauPort": ("vorschau", "VorschauPort"),
    "mm_zu_px": ("einheiten", "mm_zu_px"),
    "programmversion": ("version", "programmversion"),
    "px_je_mm": ("einheiten", "px_je_mm"),
    "px_zu_mm": ("einheiten", "px_zu_mm"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "dokument":
        from . import dokument as _datei
    elif datei == "einheiten":
        from . import einheiten as _datei
    elif datei == "fehler":
        from . import fehler as _datei
    elif datei == "einstellungen":
        from . import einstellungen as _datei
    elif datei == "seiten_port":
        from . import seiten_port as _datei
    elif datei == "silbenfarben":
        from . import silbenfarben as _datei
    elif datei == "smartart":
        from . import smartart as _datei
    elif datei == "sprechblasen":
        from . import sprechblasen as _datei
    elif datei == "version":
        from . import version as _datei
    elif datei == "vorschau":
        from . import vorschau as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
