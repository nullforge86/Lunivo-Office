"""Tür des Pakets ``framework.serienbriefe``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "adressblock_einfuegen": ("befehle", "adressblock_einfuegen"),
    "etiketten_aufbauen": ("befehle", "etiketten_aufbauen"),
    "etiketten_boegen": ("formate", "etiketten_boegen"),
    "feld_einfuegen": ("befehle", "feld_einfuegen"),
    "felder_hervorheben": ("befehle", "felder_hervorheben"),
    "felder_im_text": ("befehle", "felder_im_text"),
    "naechster_einfuegen": ("befehle", "naechster_einfuegen"),
    "regel_einfuegen": ("befehle", "regel_einfuegen"),
    "umschlag_aufbauen": ("befehle", "umschlag_aufbauen"),
    "umschlag_formate": ("formate", "umschlag_formate"),
    "zuordenbare_felder": ("befehle", "zuordenbare_felder"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "befehle":
        from . import befehle as _datei
    elif datei == "formate":
        from . import formate as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
