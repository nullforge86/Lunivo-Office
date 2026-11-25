"""Tür des Pakets ``core.objekte.wordart``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "BELEUCHTUNG": ("textfx_daten", "BELEUCHTUNG"),
    "MATERIAL": ("textfx_daten", "MATERIAL"),
    "PX": ("textfx_daten", "PX"),
    "SCHLUESSEL": ("textfx_daten", "SCHLUESSEL"),
    "WARP_FORMEN": ("textfx_daten", "WARP_FORMEN"),
    "als_text": ("textfx_daten", "als_text"),
    "aus_text": ("textfx_daten", "aus_text"),
    "hat_effekt": ("textfx_daten", "hat_effekt"),
    "leuchten_vorgaben": ("textfx_vorgaben_modell", "leuchten_vorgaben"),
    "reflektion_vorgaben": ("textfx_vorgaben_modell", "reflektion_vorgaben"),
    "schatten_vorgaben": ("textfx_vorgaben_modell", "schatten_vorgaben"),
    "wordart_vorgaben": ("textfx_vorgaben_modell", "wordart_vorgaben"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "textfx_daten":
        from . import textfx_daten as _datei
    elif datei == "textfx_vorgaben_modell":
        from . import textfx_vorgaben_modell as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
